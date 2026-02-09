from fastapi import APIRouter, Depends, HTTPException
from api import router
from api.schemas.colonyEvent import ColonyEventCreate, ColonyEventOut
from api.crud.colonyEvent import (
    list_colony_events,
    get_colony_event,
    create_colony_event,
    update_colony_event,
    delete_colony_event
)
from shared.security import require_roles

router = APIRouter(prefix="/colony-events", tags=["Colony Events"])

@router.get("", response_model=list[ColonyEventOut], dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def get_colony_events():
    """
    Docstring for get_colony_events

    Roles allowed: USER, EDITOR, ADMIN
    """
    return list_colony_events()

@router.get("/{colony_event_id}", response_model=ColonyEventOut, dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def get_one_colony_event(colony_event_id: int):
    """
    Docstring for get_one_colony_event

    Roles allowed: USER, EDITOR, ADMIN
    
    :param colony_event_id: Description
    :type colony_event_id: int
    """
    colony_event = get_colony_event(colony_event_id)
    if not colony_event:
        raise HTTPException(status_code=404, detail="Colony Event not found")
    return colony_event

@router.post("", response_model=ColonyEventOut, dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def create_new_colony_event(colony_event: ColonyEventCreate):
    """
    Docstring for create_new_colony_event

    Roles allowed: ADMIN, EDITOR
    
    :param colony_event: Description
    :type colony_event: ColonyEventCreate
    """
    return create_colony_event(colony_event.model_dump())

@router.put("/{colony_event_id}", response_model=ColonyEventOut, dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def update_existing_colony_event(colony_event_id: int, colony_event: ColonyEventCreate):
    """
    Docstring for update_existing_colony_event

    Roles allowed: ADMIN, EDITOR
    
    :param colony_event_id: Description
    :type colony_event_id: int
    :param colony_event: Description
    :type colony_event: ColonyEventCreate
    """
    updated = update_colony_event(colony_event_id, colony_event.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Colony Event not found")
    return updated

@router.delete("/{colony_event_id}", dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def delete_existing_colony_event(colony_event_id: int):
    """
    Docstring for delete_existing_colony_event

    Roles allowed: ADMIN, EDITOR
    
    :param colony_event_id: Description
    :type colony_event_id: int
    """
    if not delete_colony_event(colony_event_id):
        raise HTTPException(status_code=404, detail="Colony Event not found")
    return {"deleted": True}
