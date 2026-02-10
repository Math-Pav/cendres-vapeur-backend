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
import random
from datetime import datetime

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


@router.get("/toxicity/status")
def get_toxicity_status():
    """
    Récupère l'état actuel de la toxicité/pollution de la colonie
    Génère des données aléatoires simulant les capteurs de pollution
    
    Seuils d'alerte:
    - CRITICAL: soufre > 70% (Alerte Rouge)
    - WARNING: soufre > 50% (Alerte Orange)
    - CAUTION: soufre > 30% (Alerte Jaune)
    - NORMAL: soufre <= 30% (Normal)
    """
    
    sulfur_level = round(random.uniform(10, 95), 2)
    carbon_level = round(random.uniform(5, 80), 2)
    particulates = round(random.uniform(15, 120), 2)
    oxygen_level = round(random.uniform(15, 25), 2)
    
    alert_level = "NORMAL"
    alert_color = "green"
    
    if sulfur_level > 70:
        alert_level = "CRITICAL"
        alert_color = "red"
    elif sulfur_level > 50:
        alert_level = "WARNING"
        alert_color = "orange"
    elif sulfur_level > 30:
        alert_level = "CAUTION"
        alert_color = "yellow"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "alert_level": alert_level,
        "alert_color": alert_color,
        "pollution": {
            "sulfur": sulfur_level,
            "carbon_dioxide": carbon_level,
            "particulates": particulates,
            "oxygen": oxygen_level
        },
        "status": "OPERATIONAL" if alert_level in ["NORMAL", "CAUTION"] else "DANGEROUS"
    }
