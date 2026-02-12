from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from api.schemas.order import (
    OrderCreate, 
    OrderOut, 
    AddToCartRequest, 
    CartResponse,
    PaymentRequest,
    UpdateCartItemRequest,
    ShippingInfoRequest
)
from api.crud.order import (
    list_orders,
    get_order,
    create_order,
    update_order,
    delete_order,
    get_or_create_cart,  
    add_product_to_cart,
    remove_product_from_cart,
    update_cart_item_quantity,
    clear_cart,
    checkout_cart,
    confirm_order_details,
    process_payment,
    apply_discount_code,
    remove_discount
)
from shared.pdf_generator import generate_invoice_pdf
from shared.paypal_simulator import simulate_paypal_payment
from apps.models import OrderItem
from shared.security import require_roles

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("", response_model=list[OrderOut], dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def get_orders():
    return list_orders()

@router.get("/{order_id}", response_model=OrderOut, dependencies=[Depends(require_roles("ADMIN", "EDITOR", "USER"))])
def get_one_order(order_id: int):
    order = get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("", response_model=OrderOut)
def create_new_order(order: OrderCreate, payload = Depends(require_roles("ADMIN", "EDITOR"))):
    return create_order(order.model_dump(), user_id=payload['id'])

@router.put("/{order_id}", response_model=OrderOut)
def update_existing_order(order_id: int, order: OrderCreate, payload = Depends(require_roles("ADMIN", "EDITOR"))):
    updated = update_order(order_id, order.model_dump(), user_id=payload['id'])
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.delete("/{order_id}")
def delete_existing_order(order_id: int, payload = Depends(require_roles("ADMIN", "EDITOR"))):
    if not delete_order(order_id, user_id=payload['id']):
        raise HTTPException(status_code=404, detail="Order not found")
    return {"deleted": True}

# ======================== PANIER ========================

@router.post("/cart/add", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def add_to_cart(user_id: int, request: AddToCartRequest):
    """Ajoute un produit au panier de l'utilisateur"""
    try:
        order_item = add_product_to_cart(user_id, request.product_id, request.quantity)
        cart = order_item.order
        items = OrderItem.objects.filter(order=cart)
        
        return {
            "success": True,
            "message": "Produit ajouté au panier",
            "order_item": {
                "id": order_item.id,
                "product_id": order_item.product_id,
                "quantity": order_item.quantity,
                "unit_price_frozen": str(order_item.unit_price_frozen)
            },
            "cart": {
                "id": cart.id,
                "total_amount": str(cart.total_amount),
                "item_count": items.count()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cart/{user_id}", response_model=CartResponse, dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def get_user_cart(user_id: int):
    """Récupère le panier (commande CART) de l'utilisateur"""
    try:
        cart = get_or_create_cart(user_id)
        items = OrderItem.objects.filter(order=cart)
        
        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "status": cart.status,
            "total_amount": cart.total_amount,
            "created_at": cart.created_at,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price_frozen": item.unit_price_frozen
                }
                for item in items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/cart/{user_id}/product/{product_id}", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def update_product_quantity(user_id: int, product_id: int, request: UpdateCartItemRequest):
    """Modifie la quantité d'un produit dans le panier"""
    try:
        order_item = update_cart_item_quantity(user_id, product_id, request.quantity)
        cart = order_item.order
        items = OrderItem.objects.filter(order=cart)
        
        return {
            "success": True,
            "message": "Quantité mise à jour",
            "order_item": {
                "id": order_item.id,
                "product_id": order_item.product_id,
                "quantity": order_item.quantity,
                "unit_price_frozen": str(order_item.unit_price_frozen)
            },
            "cart": {
                "id": cart.id,
                "total_amount": str(cart.total_amount),
                "item_count": items.count()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cart/{user_id}/product/{product_id}", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def remove_from_cart(user_id: int, product_id: int):
    """Retire un produit du panier"""
    try:
        remove_product_from_cart(user_id, product_id)
        cart = get_or_create_cart(user_id)
        items = OrderItem.objects.filter(order=cart)
        
        return {
            "success": True,
            "message": "Produit retiré du panier",
            "cart": {
                "id": cart.id,
                "total_amount": str(cart.total_amount),
                "item_count": items.count()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cart/{user_id}", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def empty_cart(user_id: int):
    """Vide complètement le panier de l'utilisateur"""
    try:
        cart = clear_cart(user_id)
        
        return {
            "success": True,
            "message": "Panier vidé",
            "cart": {
                "id": cart.id,
                "total_amount": str(cart.total_amount),
                "item_count": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ======================== FLUX DE COMMANDE ========================

@router.post("/{order_id}/checkout", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def checkout_order(order_id: int):
    """
    Convertit le panier (CART) en commande (PENDING)
    Étape 1 du flux de commande
    """
    try:
        order = checkout_cart(order_id)
        return {
            "success": True,
            "message": "Panier converti en commande. Veuillez confirmer vos infos de livraison",
            "order_id": order.id,
            "status": order.status,
            "total_amount": str(order.total_amount)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{order_id}/confirm-details", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def confirm_order_info(order_id: int, shipping_info: ShippingInfoRequest):
    """
    Valide et confirme les informations de livraison/facturation
    Étape 2 du flux de commande
    Passe de PENDING à CONFIRMED
    """
    try:
        order = confirm_order_details(order_id, shipping_info.model_dump())
        return {
            "success": True,
            "message": "Infos de livraison confirmées. Prêt pour le paiement",
            "order_id": order.id,
            "status": order.status,
            "confirmed_at": order.confirmed_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{order_id}/payment", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def process_order_payment(order_id: int, request: PaymentRequest):
    """
    Traite le paiement d'une commande CONFIRMED
    Étape 3 du flux de commande
    
    Si approuvé:
    - CONFIRMED -> PAID
    - Génère le PDF de la facture
    - Crée un nouveau panier CART vide
    
    Si refusé:
    - Reste CONFIRMED
    - Permet de réessayer
    """
    try:
        payment_info = {
            'payment_method': 'PAYPAL',
            'approve': request.approve,
            'paypal_email': request.paypal_email
        }
        
        result = process_payment(order_id, payment_info)
        
        if result['success']:
            return {
                "success": True,
                "message": result['message'],
                "order_id": result['order_id'],
                "status": result['status'],
                "next_step": "Facture disponible au téléchargement"
            }
        else:
            return {
                "success": False,
                "message": result['message'],
                "order_id": result['order_id'],
                "status": result['status'],
                "next_step": "Veuillez réessayer le paiement"
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{order_id}/invoice", dependencies=[Depends(require_roles("ADMIN", "EDITOR", "USER"))])
def download_invoice(order_id: int):
    """Télécharge la facture PDF d'une commande (PAID uniquement)"""
    try:
        pdf_buffer = generate_invoice_pdf(order_id)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=facture-{order_id:05d}.pdf"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{order_id}/apply-discount", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def apply_discount(order_id: int, discount_code: str):
    """
    Applique un code de réduction à une commande
    """
    try:
        result = apply_discount_code(order_id, discount_code)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{order_id}/remove-discount", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def remove_discount_endpoint(order_id: int):
    """Retire la remise d'une commande"""
    try:
        result = remove_discount(order_id)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))