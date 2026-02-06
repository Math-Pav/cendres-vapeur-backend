from apps.models import Order, OrderItem, Product
from apps.models.customUser import CustomUser
from shared.pdf_generator import save_invoice_to_file



def list_orders():
    return Order.objects.select_related("user").all()

def get_order(order_id: int):
    return Order.objects.filter(id=order_id).first()

def create_order(data: dict):
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
    return order

def delete_order(order_id: int):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return False
    order.delete()
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
    
    # Vérifie le stock disponible
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
        # Vérifie que la quantité totale ne dépasse pas le stock
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
