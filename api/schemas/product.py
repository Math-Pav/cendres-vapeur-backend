from pydantic import BaseModel

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
    pass

class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True