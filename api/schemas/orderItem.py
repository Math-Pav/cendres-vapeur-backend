from pydantic import BaseModel
from decimal import Decimal

class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price_frozen: Decimal

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int

    class Config:
        from_attributes = True