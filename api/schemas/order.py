from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal

class OrderBase(BaseModel):
    status: str
    total_amount: Decimal
    user_id: int

class OrderCreate(OrderBase):
    pass

class ShippingInfoRequest(BaseModel):
    """Requête pour valider les infos de livraison"""
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str
    billing_address: str | None = None
    billing_city: str | None = None
    billing_postal_code: str | None = None
    billing_country: str | None = None

class OrderOut(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    shipping_address: str | None = None
    shipping_city: str | None = None
    shipping_postal_code: str | None = None
    shipping_country: str | None = None
    billing_address: str | None = None
    billing_city: str | None = None
    billing_postal_code: str | None = None
    billing_country: str | None = None
    payment_method: str | None = None
    payment_status: str | None = None
    discount_code: str | None = None
    discount_amount: Decimal = 0
    invoice_file: str | None = None
    confirmed_at: datetime | None = None
    paid_at: datetime | None = None

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