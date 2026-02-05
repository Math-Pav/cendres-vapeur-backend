from pydantic import BaseModel
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None
    created_at: datetime | None = None

class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
