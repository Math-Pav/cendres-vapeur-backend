from fastapi import APIRouter, HTTPException
from api import router
from api.schemas.user import UserCreate, UserOut
from api.crud.user import (
    list_users,
    get_user,
    create_user,
    update_user,
    delete_user
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[UserOut])
def get_users():
    return list_users()

@router.get("/{user_id}", response_model=UserOut)
def get_one_user(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=UserOut)
def create_new_user(user: UserCreate):
    return create_user(user.model_dump())

@router.put("/{user_id}", response_model=UserOut)
def update_existing_user(user_id: int, user: UserCreate):
    updated = update_user(user_id, user.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}")
def delete_existing_user(user_id: int):
    if not delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}
