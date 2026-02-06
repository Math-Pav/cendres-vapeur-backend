from fastapi import APIRouter, HTTPException
from api import router
from api.schemas.category import CategoryCreate, CategoryOut
from api.crud.category import (
    list_categories,
    get_category,
    create_category,
    update_category,
    delete_category
)

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=list[CategoryOut])
def get_categories():
    return list_categories()

@router.get("/{category_id}", response_model=CategoryOut)
def get_one_category(category_id: int):
    category = get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("", response_model=CategoryOut)
def create_new_category(category: CategoryCreate):
    return create_category(category.model_dump())

@router.put("/{category_id}", response_model=CategoryOut)
def update_existing_category(category_id: int, category: CategoryCreate):
    updated = update_category(category_id, category.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/{category_id}")
def delete_existing_category(category_id: int):
    if not delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"deleted": True}