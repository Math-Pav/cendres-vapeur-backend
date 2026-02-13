from apps.models import Order, OrderItem, Product
from apps.models.customUser import CustomUser
from shared.pdf_generator import save_invoice_to_file
from apps.classes.log import create_log
from django.utils import timezone
from django.db import models

def list_orders():
    return Order.objects.select_related("user").all()

def get_order(order_id: int):
    return Order.objects.filter(id=order_id).first()

def create_order(data: dict, user_id: int = None):
    user = CustomUser.objects.get(id=data["user_id"])
    create_log("Order created", user_id)
    return Order.objects.create(
        status=data["status"],
        total_amount=data["total_amount"],
        invoice_file=data.get("invoice_file"),
        user=user,
        created_at=data.get("created_at")
    )

def update_order(order_id: int, data: dict, user_id: int = None):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return None

    for field, value in data.items():
        if field == "user_id":
            order.user_id = value
        else:
            setattr(order, field, value)

    order.save()
    create_log("Order updated", user_id)
    return order

def delete_order(order_id: int, user_id: int = None):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return False
    order.delete()
    create_log("Order deleted", user_id)
    return True

def get_or_create_cart(user_id: int):
    """Récupère ou crée le panier (commande CART) de l'utilisateur"""
    user = CustomUser.objects.get(id=user_id)
    cart, created = Order.objects.get_or_create(
        user=user,
        status='CART',
        defaults={'total_amount': 0}
    )
    return cart

def add_product_to_cart(user_id: int, product_id: int, quantity: int):
    """Ajoute un produit au panier de l'utilisateur"""
    cart = get_or_create_cart(user_id)
    
    product = Product.objects.get(id=product_id)
    
    if product.stock < quantity:
        raise ValueError(
            f"Stock insuffisant pour '{product.name}' : "
            f"vous demandez {quantity} unités mais il n'y en a que {product.stock} en stock"
        )
    
    order_item = OrderItem.objects.filter(
        order=cart,
        product=product
    ).first()
    
    if order_item:
        total_quantity = order_item.quantity + quantity
        if product.stock < total_quantity:
            raise ValueError(
                f"Stock insuffisant pour '{product.name}' : "
                f"vous avez déjà {order_item.quantity} unité(s) et en demandez {quantity} de plus "
                f"(total {total_quantity}) mais il n'y en a que {product.stock} en stock"
            )
        order_item.quantity += quantity
        order_item.save()
    else:
        order_item = OrderItem.objects.create(
            order=cart,
            product=product,
            quantity=quantity,
            unit_price_frozen=product.current_price
        )
    
    update_cart_total(cart)
    
    return order_item

def update_cart_total(cart):
    """Met à jour le montant total du panier"""
    total = sum(
        item.quantity * item.unit_price_frozen 
        for item in cart.orderitem_set.all()
    )
    cart.total_amount = total
    cart.save()

def remove_product_from_cart(user_id: int, product_id: int):
    """Retire complètement un produit du panier"""
    cart = get_or_create_cart(user_id)
    
    order_item = OrderItem.objects.filter(
        order=cart,
        product_id=product_id
    ).first()
    
    if not order_item:
        raise ValueError(f"Produit {product_id} non trouvé dans le panier")
    
    order_item.delete()
    update_cart_total(cart)
    
    return True

def update_cart_item_quantity(user_id: int, product_id: int, new_quantity: int):
    """Met à jour la quantité d'un produit dans le panier"""
    cart = get_or_create_cart(user_id)
    product = Product.objects.get(id=product_id)
    
    if new_quantity <= 0:
        raise ValueError("La quantité doit être supérieure à 0")
    
    order_item = OrderItem.objects.filter(
        order=cart,
        product=product
    ).first()
    
    if not order_item:
        raise ValueError(f"Produit {product_id} non trouvé dans le panier")

    quantity_difference = new_quantity - order_item.quantity
    available_stock = product.stock + order_item.quantity
    
    if new_quantity > available_stock:
        raise ValueError(
            f"Stock insuffisant pour '{product.name}' : "
            f"stock disponible {available_stock}, vous demandez {new_quantity}"
        )
    
    order_item.quantity = new_quantity
    order_item.save()
    update_cart_total(cart)
    
    return order_item

def clear_cart(user_id: int):
    """Vide complètement le panier de l'utilisateur"""
    cart = get_or_create_cart(user_id)
    
    OrderItem.objects.filter(order=cart).delete()
    
    cart.total_amount = 0
    cart.save()
    
    return cart

def checkout_cart(order_id: int):
    """Convertit le panier CART en une commande PENDING pour confirmation"""
    cart = Order.objects.get(id=order_id)
    
    # Vérifier que c'est bien un panier
    if cart.status != 'CART':
        raise ValueError(f"Impossible de convertir une commande en statut {cart.status}")
    
    # Vérifier qu'il y a des articles
    if not OrderItem.objects.filter(order=cart).exists():
        raise ValueError("Le panier est vide. Impossible de passer commande")
    
    # Passer le panier en PENDING (en attente de confirmation des infos)
    cart.status = 'PENDING'
    cart.save()
    
    create_log(f"Order checkout - Order #{cart.id}", cart.user_id)
    
    return cart

def confirm_order_details(order_id: int, shipping_info: dict):
    """
    Valide et confirme les informations de livraison/facturation
    Passe la commande de PENDING à CONFIRMED
    """
    order = Order.objects.get(id=order_id)
    
    if order.status != 'PENDING':
        raise ValueError(f"Impossible de confirmer une commande en statut {order.status}")
    
    if not OrderItem.objects.filter(order=order).exists():
        raise ValueError("La commande ne contient aucun article")
    
    # Remplir les infos de livraison
    order.shipping_address = shipping_info.get('shipping_address')
    order.shipping_city = shipping_info.get('shipping_city')
    order.shipping_postal_code = shipping_info.get('shipping_postal_code')
    order.shipping_country = shipping_info.get('shipping_country')
    
    # Remplir les infos de facturation (utiliser les mêmes si pas fourni)
    order.billing_address = shipping_info.get('billing_address') or shipping_info.get('shipping_address')
    order.billing_city = shipping_info.get('billing_city') or shipping_info.get('shipping_city')
    order.billing_postal_code = shipping_info.get('billing_postal_code') or shipping_info.get('shipping_postal_code')
    order.billing_country = shipping_info.get('billing_country') or shipping_info.get('shipping_country')
    
    # Passer au statut CONFIRMED en attente de paiement
    order.status = 'CONFIRMED'
    order.confirmed_at = timezone.now()
    order.save()
    
    create_log(f"Order details confirmed - Order #{order.id}", order.user_id)
    
    return order

def process_payment(order_id: int, payment_info: dict):
    """
    Traite le paiement d'une commande
    Si approuvé: CONFIRMED -> PAID, génère PDF, crée nouveau panier
    Si refusé: reste CONFIRMED
    """
    order = Order.objects.get(id=order_id)
    
    if order.status != 'CONFIRMED':
        raise ValueError(f"Impossible de payer une commande en statut {order.status}")
    
    # Enregistrer les infos de paiement
    order.payment_method = payment_info.get('payment_method', 'PAYPAL')
    order.payment_status = 'APPROVED' if payment_info.get('approve', False) else 'REJECTED'
    
    if payment_info.get('approve', False):
        # Paiement approuvé
        order.status = 'PAID'
        order.paid_at = timezone.now()
        order.save()
        
        # Générer la facture PDF
        save_invoice_to_file(order_id)
        
        create_log(f"Order paid - Order #{order.id}", order.user_id)
        
        # Créer un nouveau panier CART vide pour l'utilisateur
        Order.objects.get_or_create(
            user=order.user,
            status='CART',
            defaults={'total_amount': 0}
        )
        
        return {
            'success': True,
            'message': 'Paiement approuvé et commande confirmée',
            'order_id': order.id,
            'status': 'PAID'
        }
    else:
        # Paiement refusé
        order.save()
        create_log(f"Order payment rejected - Order #{order.id}", order.user_id)
        
        return {
            'success': False,
            'message': 'Paiement refusé. Veuillez réessayer',
            'order_id': order.id,
            'status': 'CONFIRMED'
        }

DISCOUNT_CODES = {
    'WELCOME10': 10,     
    'PROMO15': 15,        
    'SPECIAL20': 20,        
    'VIP25': 25,            
    'NEWUSER5': 5,          
}

def apply_discount_code(order_id: int, code: str):
    """
    Applique un code de réduction à une commande
    Retourne la réduction appliquée
    """
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return {
            'success': False,
            'message': 'Commande non trouvée'
        }
    
    code = code.upper().strip()
    
    if code not in DISCOUNT_CODES:
        return {
            'success': False,
            'message': 'Code de réduction invalide'
        }
    
    if order.status not in ['CART', 'PENDING']:
        return {
            'success': False,
            'message': 'Impossible d\'appliquer une réduction à cette commande'
        }
    
    percentage = DISCOUNT_CODES[code]
    
    items_total = sum(
        item.quantity * item.unit_price_frozen 
        for item in order.orderitem_set.all()
    )
    
    discount_amount = (items_total * percentage) / 100
    new_total = items_total - discount_amount
    
    order.discount_code = code
    order.discount_amount = discount_amount
    order.total_amount = new_total
    order.save()
    
    return {
        'success': True,
        'message': f'Code {code} appliqué avec succès',
        'discount_code': code,
        'discount_percentage': percentage,
        'discount_amount': float(discount_amount),
        'subtotal': float(items_total),
        'total_amount': float(new_total),
        'savings': f'{percentage}%'
    }

def remove_discount(order_id: int):
    """Retire la remise d'une commande"""
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return {
            'success': False,
            'message': 'Commande non trouvée'
        }
    
    if order.status not in ['CART', 'PENDING']:
        return {
            'success': False,
            'message': 'Impossible de retirer une réduction de cette commande'
        }
    
    items_total = sum(
        item.quantity * item.unit_price_frozen 
        for item in order.orderitem_set.all()
    )
    
    order.discount_code = None
    order.discount_amount = 0
    order.total_amount = items_total
    order.save()
    
    return {
        'success': True,
        'message': 'Remise supprimée',
        'total_amount': float(items_total)
    }

def get_admin_stats():
    """
    Récupère les statistiques globales pour le dashboard admin
    Calcule les revenus, nombre de commandes par statut, moyennes, etc.
    """
    from decimal import Decimal
    
    # Récupérer toutes les commandes
    all_orders = Order.objects.all()
    paid_orders = Order.objects.filter(status='PAID')
    pending_orders = Order.objects.filter(status='PENDING')
    confirmed_orders = Order.objects.filter(status='CONFIRMED')
    cart_orders = Order.objects.filter(status='CART')
    shipped_orders = Order.objects.filter(status='SHIPPED')
    
    # Calculs des revenus
    total_revenue = sum(order.total_amount for order in paid_orders)
    total_discount_given = sum(order.discount_amount for order in paid_orders)
    
    # Nombre de commandes par statut
    stats_by_status = {
        'CART': cart_orders.count(),
        'PENDING': pending_orders.count(),
        'CONFIRMED': confirmed_orders.count(),
        'PAID': paid_orders.count(),
        'SHIPPED': shipped_orders.count(),
        'TOTAL': all_orders.count()
    }
    
    # Calculs des moyennes et min/max
    if paid_orders.exists():
        paid_amounts = [order.total_amount for order in paid_orders]
        average_revenue = total_revenue / len(paid_amounts)
        min_revenue = min(paid_amounts)
        max_revenue = max(paid_amounts)
    else:
        average_revenue = Decimal('0')
        min_revenue = Decimal('0')
        max_revenue = Decimal('0')
    
    # Revenu moyen par article
    total_items = sum(
        OrderItem.objects.filter(order__status='PAID').aggregate(
            total=models.Sum('quantity')
        ).get('total') or 0
        for _ in [1]
    )
    total_items_count = OrderItem.objects.filter(order__status='PAID').count()
    
    # Top clients (par revenu dépensé)
    from django.db.models import Sum
    top_clients = []
    client_stats = Order.objects.filter(status='PAID').values('user__id', 'user__username', 'user__email').annotate(
        total_spent=Sum('total_amount'),
        order_count=models.Count('id')
    ).order_by('-total_spent')[:5]
    
    for client in client_stats:
        top_clients.append({
            'user_id': client['user__id'],
            'username': client['user__username'],
            'email': client['user__email'],
            'total_spent': float(client['total_spent']),
            'order_count': client['order_count']
        })
    
    # Top produits vendus
    from django.db.models import F, FloatField
    from django.db.models.functions import Cast
    
    top_products = []
    product_stats = OrderItem.objects.filter(
        order__status='PAID'
    ).values('product__id', 'product__name', 'product__current_price').annotate(
        total_quantity=models.Sum('quantity'),
        total_revenue=models.Sum(F('quantity') * F('unit_price_frozen'), output_field=models.DecimalField())
    ).order_by('-total_quantity')[:5]
    
    for product in product_stats:
        top_products.append({
            'product_id': product['product__id'],
            'product_name': product['product__name'],
            'current_price': float(product['product__current_price']),
            'total_quantity_sold': product['total_quantity'],
            'total_revenue': float(product['total_revenue'] or 0)
        })
    
    return {
        'success': True,
        'revenue': {
            'total_revenue': float(total_revenue),
            'total_discount_given': float(total_discount_given),
            'average_revenue_per_order': float(average_revenue),
            'min_revenue': float(min_revenue),
            'max_revenue': float(max_revenue)
        },
        'orders': {
            'total_orders': stats_by_status['TOTAL'],
            'by_status': {
                'cart': stats_by_status['CART'],
                'pending': stats_by_status['PENDING'],
                'confirmed': stats_by_status['CONFIRMED'],
                'paid': stats_by_status['PAID'],
                'shipped': stats_by_status['SHIPPED']
            }
        },
        'top_clients': top_clients,
        'top_products': top_products,
        'summary': {
            'total_customers_who_paid': paid_orders.values('user').distinct().count(),
            'average_items_per_paid_order': round(total_items_count / stats_by_status['PAID'], 2) if stats_by_status['PAID'] > 0 else 0
        }
    }