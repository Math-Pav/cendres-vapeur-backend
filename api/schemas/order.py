from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal

class OrderBase(BaseModel):
    status: str
    total_amount: Decimal
    invoice_file: str | None = None
    user_id: int

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("invoice_file", mode="before")
    @classmethod
    def convert_file_field(cls, v):
        if v is None:
            return None
        if hasattr(v, "name"):
            return str(v.name)
        return str(v)


class AddToCartRequest(BaseModel):
    """Requête pour ajouter un produit au panier"""
    product_id: int
    quantity: int = 1


class UpdateCartItemRequest(BaseModel):
    """Requête pour modifier la quantité d'un article du panier"""
    quantity: int

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    """Réponse pour un article du panier"""
    id: int
    product_id: int
    quantity: int
    unit_price_frozen: Decimal

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Réponse du panier avec ses articles"""
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: list[CartItemResponse] = []

    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """Requête pour simuler un paiement PayPal"""
    paypal_email: str
    approve: bool = True
