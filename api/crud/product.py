from apps.models import Product, Category
from shared.price_fluctuation import PriceFluctuation
from decimal import Decimal
from apps.classes.log import create_log

def list_products():
    return Product.objects.all()

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