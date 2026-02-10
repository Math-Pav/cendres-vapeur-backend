from fastapi import APIRouter, Depends, HTTPException
from api import router
from api.schemas.user import UserCreate, UserOut
from api.crud.user import (
    list_users,
    list_users_advanced,
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

@router.get("/search", response_model=dict, dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def search_users(search: str = None, role: str = None, page: int = 1, limit: int = 20):
    """
    Recherche et filtre les utilisateurs avec pagination
    
    Query params:
    - search: Recherche par username ou email
    - role: Filtrer par rôle (ADMIN, EDITOR, USER, INVITE)
    - page: Numéro de page (default: 1)
    - limit: Résultats par page (default: 20, max: 100)
    
    Roles allowed: ADMIN, EDITOR
    """
    result = list_users_advanced(search=search, role=role, page=page, limit=limit)
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Error fetching users'))
    return result

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

@router.post("", response_model=UserOut)
def create_new_user(user: UserCreate, payload = Depends(require_roles("ADMIN"))):
    """
    Docstring for create_new_user

    Roles allowed: ADMIN
    
    :param user: Description
    :type user: UserCreate
    """
    return create_user(user.model_dump(), user_id=payload['id'])

@router.put("/{user_id}", response_model=UserOut)
def update_existing_user(user_id: int, user: UserCreate, payload = Depends(require_roles("ADMIN"))):
    """
    Docstring for update_existing_user

    Roles allowed: ADMIN
    
    :param user_id: Description
    :type user_id: int
    :param user: Description
    :type user: UserCreate
    """
    updated = update_user(user_id, user.model_dump(), current_user_id=payload['id'])
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}")
def delete_existing_user(user_id: int, payload = Depends(require_roles("ADMIN"))):
    """
    Docstring for delete_existing_user

    Roles allowed: ADMIN
    
    :param user_id: Description
    :type user_id: int
    """
    if not delete_user(user_id, current_user_id=payload['id']):
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}
