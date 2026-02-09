from fastapi import APIRouter, Depends, HTTPException
from api import router
from api.schemas.shiftNote import ShiftNoteCreate, ShiftNoteOut
from api.crud.shiftNote import (
    list_shift_notes,
    get_shift_note,
    create_shift_note,
    update_shift_note,
    delete_shift_note
)
from shared.security import require_roles

router = APIRouter(prefix="/shift-notes", tags=["Shift Notes"])

@router.get("", response_model=list[ShiftNoteOut], dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_shift_notes():
    return list_shift_notes()

@router.get("/{shift_note_id}", response_model=ShiftNoteOut, dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_one_shift_note(shift_note_id: int):
    shift_note = get_shift_note(shift_note_id)
    if not shift_note:
        raise HTTPException(status_code=404, detail="Shift Note not found")
    return shift_note

@router.post("", response_model=ShiftNoteOut, dependencies=[Depends(require_roles("EDITOR" ,"ADMIN"))])
def create_new_shift_note(shift_note: ShiftNoteCreate):
    return create_shift_note(shift_note.model_dump())

@router.put("/{shift_note_id}", response_model=ShiftNoteOut, dependencies=[Depends(require_roles("EDITOR" ,"ADMIN"))])
def update_existing_shift_note(shift_note_id: int, shift_note: ShiftNoteCreate):
    updated = update_shift_note(shift_note_id, shift_note.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Shift Note not found")
    return updated

@router.delete("/{shift_note_id}", dependencies=[Depends(require_roles("ADMIN"))])
def delete_existing_shift_note(shift_note_id: int):
    if not delete_shift_note(shift_note_id):
        raise HTTPException(status_code=404, detail="Shift Note not found")
    return {"deleted": True}