from fastapi import APIRouter, Depends, HTTPException
from api.schemas.orderItem import OrderItemCreate, OrderItemOut
from api.crud.orderItem import (
    list_order_items,
    get_order_item,
    create_order_item,
    update_order_item,
    delete_order_item
)
from shared.security import require_roles

router = APIRouter(prefix="/order-items", tags=["OrderItems"])

@router.get("", response_model=list[OrderItemOut])
def get_order_items():
    return list_order_items()

@router.get("/{order_item_id}", response_model=OrderItemOut,dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_one_order_item(order_item_id: int):
    order_item = get_order_item(order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return order_item

@router.post("", response_model=OrderItemOut, dependencies=[Depends(require_roles("EDITOR" ,"ADMIN"))])
def create_new_order_item(order_item: OrderItemCreate):
    return create_order_item(order_item.model_dump())

@router.put("/{order_item_id}", response_model=OrderItemOut, dependencies=[Depends(require_roles("EDITOR" ,"ADMIN"))])
def update_existing_order_item(order_item_id: int, order_item: OrderItemCreate):
    updated = update_order_item(order_item_id, order_item.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return updated

@router.delete("/{order_item_id}", dependencies=[Depends(require_roles("ADMIN"))])
def delete_existing_order_item(order_item_id: int):
    if not delete_order_item(order_item_id):
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return {"deleted": True}