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