from fastapi import APIRouter, HTTPException
from api.schemas.order import OrderCreate, OrderOut
from api.crud.order import (
    list_orders,
    get_order,
    create_order,
    update_order,
    delete_order
)

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
