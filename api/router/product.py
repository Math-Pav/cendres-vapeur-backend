from fastapi import APIRouter, HTTPException
from api import router
from api.schemas.product import ProductCreate, ProductOut
from api.crud.product import (
    list_products,
    get_product,
    create_product,
    update_product,
    delete_product
)

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=list[ProductOut])
def get_products():
    return list_products()

@router.get("/{product_id}", response_model=ProductOut)
def get_one_product(product_id: int):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("", response_model=ProductOut)
def create_new_product(product: ProductCreate):
    return create_product(product.model_dump())

@router.put("/{product_id}", response_model=ProductOut)
def update_existing_product(product_id: int, product: ProductCreate):
    updated = update_product(product_id, product.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}")
def delete_existing_product(product_id: int):
    if not delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": True}

