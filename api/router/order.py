from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from api.schemas.order import (
    OrderCreate, 
    OrderOut, 
    AddToCartRequest, 
    CartResponse
)
from api.crud.order import (
    list_orders,
    get_order,
    create_order,
    update_order,
    delete_order,
    get_or_create_cart,
    add_product_to_cart,
    finalize_order
)
from shared.pdf_generator import generate_invoice_pdf
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


@router.post("/{order_id}/finalize")
def finalize_order_endpoint(order_id: int):
    """Finalise une commande : génère la facture et change le statut en PAID"""
    try:
        order = finalize_order(order_id)
        return {
            "success": True,
            "message": "Commande finalisée",
            "order": {
                "id": int(order.id),
                "user_id": int(order.user_id),
                "status": str(order.status),
                "total_amount": float(order.total_amount),
                "invoice_file": str(order.invoice_file) if order.invoice_file else "",
                "created_at": order.created_at.isoformat() if order.created_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))