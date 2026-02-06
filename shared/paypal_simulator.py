from apps.models import Order, OrderItem
from django.utils import timezone
import uuid


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
