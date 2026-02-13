from pydantic import BaseModel, field_validator

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    image_url: str | None = None
    category_id: int
    stock: int
    base_price: float
    current_price: float
    popularity_score: float

class ProductCreate(ProductBase):
    @field_validator('stock')
    @classmethod
    def validate_stock(cls, v):
        if v is None or v <= 0:
            raise ValueError('Le stock doit être supérieur à 0')
        return v
    
    @field_validator('base_price')
    @classmethod
    def validate_base_price(cls, v):
        if v is None or v <= 0:
            raise ValueError('Le prix de base doit être supérieur à 0')
        return v

class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True