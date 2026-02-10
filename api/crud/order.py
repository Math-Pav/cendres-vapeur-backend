from apps.models import Order, OrderItem, Product
from apps.models.customUser import CustomUser
from shared.pdf_generator import save_invoice_to_file



def list_orders():
    return Order.objects.select_related("user").all()

def get_order(order_id: int):
    return Order.objects.filter(id=order_id).first()

def create_order(data: dict):
    user = User.objects.get(id=data["user_id"])
    create_log("Order created", data["user_id"])
    user = CustomUser.objects.get(id=data["user_id"])
    return Order.objects.create(
        status=data["status"],
        total_amount=data["total_amount"],
        invoice_file=data.get("invoice_file"),
        user=user,
        created_at=data.get("created_at")
    )

def update_order(order_id: int, data: dict):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return None

    for field, value in data.items():
        if field == "user_id":
            order.user_id = value
        else:
            setattr(order, field, value)

    order.save()
    create_log("Order updated", data["user_id"])
    return order

def delete_order(order_id: int):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return False
    order.delete()
    create_log("Order deleted", data["user_id"])
    return True


def get_or_create_cart(user_id: int):
    """Récupère ou crée le panier (commande PENDING) de l'utilisateur"""
    user = CustomUser.objects.get(id=user_id)
    cart, created = Order.objects.get_or_create(
        user=user,
        status='PENDING',
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


def finalize_order(order_id: int):
    """
    Finalise une commande (PENDING -> PAID) et génère la facture
    Crée une nouvelle commande PENDING pour le prochain panier
    """
    order = Order.objects.get(id=order_id)
    
    if order.status != 'PENDING':
        raise ValueError("Seules les commandes PENDING peuvent être finalisées")
    
    if not OrderItem.objects.filter(order=order).exists():
        raise ValueError("La commande ne contient aucun article")
    
    save_invoice_to_file(order_id)
    
    order.status = 'PAID'
    order.save()
    
    new_cart = Order.objects.create(
        user=order.user,
        status='PENDING',
        total_amount=0
    )
    
    return order


# Codes de réduction disponibles
DISCOUNT_CODES = {
    'WELCOME10': 10,        # 10% de réduction
    'PROMO15': 15,          # 15% de réduction
    'SPECIAL20': 20,        # 20% de réduction
    'VIP25': 25,            # 25% de réduction
    'NEWUSER5': 5,          # 5% de réduction
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
    
    if order.status != 'PENDING':
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
    
    if order.status != 'PENDING':
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
