from apps.models import Order, OrderItem, Product
from django.utils import timezone
import uuid


def verify_stock_availability(order_id: int):
    """
    Vérifie que tous les produits du panier ont suffisamment de stock
    Retourne True si tout est OK, sinon lève une exception
    """
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    for item in order_items:
        if item.product.stock < item.quantity:
            raise ValueError(
                f"Stock insuffisant pour '{item.product.name}' : "
                f"vous avez demandé {item.quantity} unités mais il n'y en a que {item.product.stock} en stock"
            )
    
    return True

def update_product_stocks(order_id: int):
    """
    Met à jour les stocks des produits après un paiement approuvé
    Décrémente le stock de chaque produit selon la quantité commandée
    """
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    for item in order_items:
        product = item.product
        product.stock -= item.quantity
        product.save()

def simulate_paypal_payment(order_id: int, paypal_email: str, approve: bool = True):
    """
    Simule un paiement PayPal complet
    Si approve=True : 
      - Approuve le paiement
      - Change le statut en PAID
      - Génère la facture
      - Crée un nouveau panier PENDING
    Si approve=False : refuse le paiement (statut reste PENDING)
    """
    from shared.pdf_generator import save_invoice_to_file
    
    order = Order.objects.get(id=order_id)
    
    if order.status != 'PENDING':
        raise ValueError(f"La commande a le statut {order.status}, ne peut pas être payée")
    
    if not OrderItem.objects.filter(order=order).exists():
        raise ValueError("Le panier est vide")
    
    if approve:
        verify_stock_availability(order_id)
        
        update_product_stocks(order_id)
        
        save_invoice_to_file(order_id)
        
        order.status = 'PAID'
        order.save()
        
        new_cart = Order.objects.create(
            user=order.user,
            status='PENDING',
            total_amount=0
        )
        
        transaction_id = f"PAYPAL-{uuid.uuid4().hex.upper()[:12]}"
        
        return {
            "success": True,
            "message": "Paiement approuvé - Facture générée",
            "payment": {
                "transaction_id": transaction_id,
                "paypal_email": paypal_email,
                "amount": float(order.total_amount),
                "status": "COMPLETED"
            },
            "order": {
                "id": int(order.id),
                "status": str(order.status),
                "invoice_file": str(order.invoice_file) if order.invoice_file else "",
                "total_amount": float(order.total_amount),
                "created_at": order.created_at.isoformat() if order.created_at else None
            },
            "new_cart": {
                "id": int(new_cart.id),
                "user_id": int(new_cart.user_id),
                "status": str(new_cart.status),
                "message": "Un nouveau panier a été créé pour vous"
            }
        }
    else:
        return {
            "success": False,
            "message": "Paiement refusé",
            "reason": "Carte refusée par la banque",
            "order": {
                "id": int(order.id),
                "status": str(order.status),
                "total_amount": float(order.total_amount)
            }
        }
