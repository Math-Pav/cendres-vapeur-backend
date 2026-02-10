from apps.models import Product, Category
from shared.price_fluctuation import PriceFluctuation
from decimal import Decimal
from apps.classes.log import create_log

def list_products():
    return Product.objects.all()

def list_products_advanced(search: str = None, category_id: int = None, min_price: float = None, 
                          max_price: float = None, sort: str = 'id', order: str = 'asc', 
                          page: int = 1, limit: int = 20):
    """
    Liste les produits avec filtres, recherche, tri et pagination
    
    Args:
        search: Recherche par nom ou description
        category_id: Filtrer par catégorie (ID)
        min_price: Prix minimum
        max_price: Prix maximum
        sort: Champ de tri (id, name, price, popularity, stock, purchase_count)
        order: Ordre de tri (asc, desc)
        page: Numéro de page (default: 1)
        limit: Nombre de résultats par page (default: 20, max: 100)
    """
    query = Product.objects.all()
    
    if category_id:
        query = query.filter(category_id=category_id)
    
    if search:
        from django.db.models import Q
        query = query.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    if min_price is not None:
        query = query.filter(current_price__gte=min_price)
    if max_price is not None:
        query = query.filter(current_price__lte=max_price)
    
    sort_field = 'id'
    if sort == 'name':
        sort_field = 'name'
    elif sort == 'price':
        sort_field = 'current_price'
    elif sort == 'popularity':
        sort_field = 'popularity_score'
    elif sort == 'stock':
        sort_field = 'stock'
    elif sort == 'purchase_count':
        sort_field = 'purchase_count'
    
    if order.lower() == 'desc':
        sort_field = '-' + sort_field
    
    query = query.order_by(sort_field)
    
    limit = min(int(limit), 100) 
    page = max(int(page), 1) 
    offset = (page - 1) * limit
    
    total_count = query.count()
    products = query[offset:offset + limit]
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category_id': product.category_id,
            'category_name': product.category.name,
            'stock': product.stock,
            'base_price': float(product.base_price),
            'current_price': float(product.current_price),
            'popularity_score': product.popularity_score,
            'purchase_count': product.purchase_count,
            'view_count': product.view_count,
            'image': product.image.url if product.image else None
        })
    
    return {
        'success': True,
        'pagination': {
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'total_pages': (total_count + limit - 1) // limit
        },
        'products': products_list
    }

def get_product(product_id: int):
    return Product.objects.filter(id=product_id).first()

def create_product(data: dict):
    category = Category.objects.get(id=data["category_id"])
    
    stock = data["stock"]
    
    create_log("Product created", data["name"])
    
    return Product.objects.create(
        name=data["name"],
        description=data.get("description"),
        stock=stock,
        image=data.get("image_url"),
        category=category,
        base_price=data["base_price"],
        current_price=data["base_price"],
        popularity_score=data.get("popularity_score", 0),
        base_stock=stock,
        view_count=0,
        purchase_count=0,
        price_change_percentage=0.0
    )

def update_product(product_id: int, data: dict):
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return None

    for field, value in data.items():
        if field != 'current_price':
            setattr(product, field, value)

    product.save()
    create_log("Product updated", product.name)
    return product

def delete_product(product_id: int):
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return False
    product.delete()
    create_log("Product deleted", product.name)
    return True

def record_product_view(product_id: int):
    """
    Enregistre une consultation d'un produit et recalcule le prix
    Appeler ceci chaque fois qu'un client consulte un produit
    """
    try:
        product = Product.objects.get(id=product_id)
        
        product.view_count += 1
        
        result = PriceFluctuation.calculate_new_price(
            base_price=float(product.base_price),
            current_price=float(product.current_price),
            current_stock=product.stock,
            base_stock=product.base_stock,
            view_count=product.view_count,
            purchase_count=product.purchase_count
        )
        
        product.previous_price = Decimal(str(result['old_price']))
        product.current_price = Decimal(str(result['new_price']))
        product.price_change_percentage = result['price_change_percent']
        product.save()
        
        return {
            'success': True,
            'product_id': product_id,
            'product_name': product.name,
            'old_price': result['old_price'],
            'new_price': result['new_price'],
            'price_change_percent': result['price_change_percent'],
            'indicator': result['indicator'],
            'supply_ratio': result['supply_ratio'],
            'demand': result['demand'],
            'stock': result['stock'],
            'view_count': product.view_count
        }
    
    except Product.DoesNotExist:
        return {'success': False, 'error': 'Product not found'}

def record_product_purchase(product_id: int, quantity: int = 1):
    """
    Enregistre un achat et recalcule le prix
    Réduit le stock et augmente la demande (achat pèse 3x plus)
    """
    try:
        product = Product.objects.get(id=product_id)
        
        if product.stock < quantity:
            return {
                'success': False,
                'error': f'Insufficient stock. Available: {product.stock}, Requested: {quantity}'
            }
        
        product.purchase_count += quantity
        product.stock -= quantity
        
        result = PriceFluctuation.calculate_new_price(
            base_price=float(product.base_price),
            current_price=float(product.current_price),
            current_stock=product.stock,
            base_stock=product.base_stock,
            view_count=product.view_count,
            purchase_count=product.purchase_count
        )
        
        product.previous_price = Decimal(str(result['old_price']))
        product.current_price = Decimal(str(result['new_price']))
        product.price_change_percentage = result['price_change_percent']
        product.save()
        
        return {
            'success': True,
            'product_id': product_id,
            'product_name': product.name,
            'quantity_purchased': quantity,
            'old_price': result['old_price'],
            'new_price': result['new_price'],
            'price_change_percent': result['price_change_percent'],
            'indicator': result['indicator'],
            'supply_ratio': result['supply_ratio'],
            'demand': result['demand'],
            'stock_remaining': product.stock,
            'purchase_count': product.purchase_count
        }
    
    except Product.DoesNotExist:
        return {'success': False, 'error': 'Product not found'}


def get_product_price_info(product_id: int):
    """
    Récupère les infos complètes du prix et de la fluctuation d'un produit
    Pour afficher le tableau de bord
    """
    try:
        product = Product.objects.get(id=product_id)
        
        demand = PriceFluctuation.calculate_demand(product.view_count, product.purchase_count)
        supply_ratio = PriceFluctuation.calculate_supply_ratio(
            product.stock,
            product.base_stock,
            demand
        )
        
        return {
            'success': True,
            'product_id': product.id,
            'product_name': product.name,
            'base_price': float(product.base_price),
            'current_price': float(product.current_price),
            'previous_price': float(product.previous_price),
            'price_change_percent': float(product.price_change_percentage),
            'indicator': PriceFluctuation.get_trend_indicator(
                float(product.price_change_percentage)
            ),
            'demand': int(demand),
            'supply_ratio': float(supply_ratio),
            'stock': product.stock,
            'base_stock': product.base_stock,
            'view_count': product.view_count,
            'purchase_count': product.purchase_count,
            'last_update': product.last_price_update.isoformat()
        }
    
    except Product.DoesNotExist:
        return {'success': False, 'error': 'Product not found'}


def get_product_votes(product_id: int):
    """
    Récupère tous les votes/notes/commentaires d'un produit
    Retourne les détails de chaque vote avec infos sur l'utilisateur
    """
    try:
        product = Product.objects.get(id=product_id)
        from apps.models.vote import Vote
        
        votes = Vote.objects.filter(product=product).select_related('user').order_by('-created_at')
        
        votes_list = []
        for vote in votes:
            votes_list.append({
                'vote_id': vote.id,
                'user_id': vote.user.id,
                'username': vote.user.username,
                'user_avatar': vote.user.avatar_url,
                'note': vote.note,
                'comment': vote.comment,
                'like': vote.like,
                'created_at': vote.created_at.isoformat()
            })
        
        total_votes = len(votes_list)
        total_likes = sum(1 for v in votes_list if v['like'])
        average_note = sum(v['note'] for v in votes_list) / total_votes if total_votes > 0 else 0
        
        return {
            'success': True,
            'product_id': product_id,
            'product_name': product.name,
            'total_votes': total_votes,
            'total_likes': total_likes,
            'average_note': round(average_note, 2),
            'votes': votes_list
        }
    
    except Product.DoesNotExist:
        return {'success': False, 'error': 'Product not found'}


def get_product_likes_count(product_id: int):
    """
    Récupère le nombre de likes d'un produit
    Retourne aussi les statistiques rapides
    """
    try:
        product = Product.objects.get(id=product_id)
        from apps.models.vote import Vote
        
        total_votes = Vote.objects.filter(product=product).count()
        total_likes = Vote.objects.filter(product=product, like=True).count()
        
        voted_users = Vote.objects.filter(product=product).values_list('user__username', flat=True)
        
        return {
            'success': True,
            'product_id': product_id,
            'product_name': product.name,
            'total_votes': total_votes,
            'total_likes': total_likes,
            'like_percentage': round((total_likes / total_votes * 100), 2) if total_votes > 0 else 0,
            'users_who_voted': list(voted_users)
        }
    
    except Product.DoesNotExist:
        return {'success': False, 'error': 'Product not found'}


def get_top_products_by_sales(limit: int = 5):
    """
    Récupère les N produits les plus vendus
    Trié par purchase_count décroissant
    Inclut: revenu généré, stock restant, prix
    """
    try:
        top_products = Product.objects.all().order_by('-purchase_count')[:limit]
        
        products_list = []
        for product in top_products:
            revenue = float(product.purchase_count * product.current_price)
            products_list.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'category': product.category.name,
                'stock': product.stock,
                'base_stock': product.base_stock,
                'base_price': float(product.base_price),
                'current_price': float(product.current_price),
                'purchase_count': product.purchase_count,
                'view_count': product.view_count,
                'revenue_generated': revenue,
                'popularity_score': product.popularity_score,
                'price_change_percent': product.price_change_percentage
            })
        
        total_revenue = sum(p['revenue_generated'] for p in products_list)
        total_purchases = sum(p['purchase_count'] for p in products_list)
        
        return {
            'success': True,
            'limit': limit,
            'top_products': products_list,
            'summary': {
                'total_revenue': round(total_revenue, 2),
                'total_purchases': total_purchases,
                'average_revenue_per_product': round(total_revenue / len(products_list), 2) if products_list else 0
            }
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}