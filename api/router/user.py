from fastapi import APIRouter, Depends, HTTPException
from api import router
from api.schemas.user import UserCreate, UserOut
from api.crud.user import (
    list_users,
    get_user,
    create_user,
    update_user,
    delete_user
)
from shared.security import require_roles

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[UserOut], dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def get_users():
    """
    Docstring for get_users
    Roles allowed: ADMIN, EDITOR
    Return a list of all users.
    """
    return list_users()

@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def get_one_user(user_id: int):
    """
    Docstring for get_one_user

    Roles allowed: ADMIN, EDITOR
    
    :param user_id: Description\n
    :type user_id: int
    """
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=UserOut, dependencies=[Depends(require_roles("ADMIN"))])
def create_new_user(user: UserCreate):
    """
    Docstring for create_new_user

    Roles allowed: ADMIN
    
    :param user: Description
    :type user: UserCreate
    """
    return create_user(user.model_dump())

@router.put("/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles("ADMIN"))])
def update_existing_user(user_id: int, user: UserCreate):
    """
    Docstring for update_existing_user

    Roles allowed: ADMIN
    
    :param user_id: Description
    :type user_id: int
    :param user: Description
    :type user: UserCreate
    """
    updated = update_user(user_id, user.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}", dependencies=[Depends(require_roles("ADMIN"))])
def delete_existing_user(user_id: int):
    """
    Docstring for delete_existing_user

    Roles allowed: ADMIN
    
    :param user_id: Description
    :type user_id: int
    """
    if not delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}
