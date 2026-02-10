from fastapi import APIRouter, Depends, HTTPException
from api import router
from api.schemas.category import CategoryCreate, CategoryOut
from shared.security import require_roles
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
    """
    Return a list of all categories.
    """
    return list_categories()

@router.get("/{category_id}", response_model=CategoryOut)
def get_one_category(category_id: int):
    """
    Docstring for get_one_category

    return a single category by its ID.
    
    :param category_id: Description\n
    :type category_id: int
    """
    category = get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("", response_model=CategoryOut, dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def create_new_category(category: CategoryCreate):
    """
    Docstring for create_new_category

    Roles allowed: USER, EDITOR, ADMIN

    Create a new category with the provided data.
    
    :param category: Description\n
    :type category: CategoryCreate
    """
    return create_category(category.model_dump())

@router.put("/{category_id}", response_model=CategoryOut, dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def update_existing_category(category_id: int, category: CategoryCreate):
    """
    Docstring for update_existing_category

    Roles allowed: ADMIN, EDITOR
    
    :param category_id: Description\n
    :type category_id: int\n
    :param category: Description\n
    :type category: CategoryCreate
    """
    updated = update_category(category_id, category.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/{category_id}", dependencies=[Depends(require_roles("ADMIN"))])
def delete_existing_category(category_id: int):
    """
    Docstring for delete_existing_category

    Roles allowed: ADMIN
    
    :param category_id: Description\n
    :type category_id: int
    """
    if not delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"deleted": True}