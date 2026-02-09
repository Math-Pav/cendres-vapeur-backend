from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from api.schemas.order import (
    OrderCreate, 
    OrderOut, 
    AddToCartRequest, 
    CartResponse,
    PaymentRequest,
    UpdateCartItemRequest
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
    clear_cart
)
from shared.pdf_generator import generate_invoice_pdf
from shared.paypal_simulator import simulate_paypal_payment
from apps.models import OrderItem

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("", response_model=list[OrderOut])
def get_orders():
    return list_orders()

@router.get("/{order_id}", response_model=OrderOut)
def get_one_order(order_id: int):
    order = get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("", response_model=OrderOut)
def create_new_order(order: OrderCreate):
    return create_order(order.model_dump())

@router.put("/{order_id}", response_model=OrderOut)
def update_existing_order(order_id: int, order: OrderCreate):
    updated = update_order(order_id, order.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.delete("/{order_id}")
def delete_existing_order(order_id: int):
    if not delete_order(order_id):
        raise HTTPException(status_code=404, detail="Order not found")
    return {"deleted": True}


@router.post("/cart/add")
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


@router.get("/cart/{user_id}", response_model=CartResponse)
def get_user_cart(user_id: int):
    """Récupère le panier (commande PENDING) de l'utilisateur"""
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


@router.put("/cart/{user_id}/product/{product_id}")
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


@router.delete("/cart/{user_id}/product/{product_id}")
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


@router.delete("/cart/{user_id}")
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


@router.get("/{order_id}/invoice")
def download_invoice(order_id: int):
    """Télécharge la facture PDF d'une commande"""
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


@router.post("/{order_id}/payment")
def process_paypal_payment(order_id: int, request: PaymentRequest):
    """
    Simule un paiement PayPal
    Si approve=true : approuve le paiement, génère la facture et crée un nouveau panier
    Si approve=false : refuse le paiement
    """
    try:
        result = simulate_paypal_payment(order_id, request.paypal_email, request.approve)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
