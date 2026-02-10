from apps.models import ShiftNote
from apps.classes.log import create_log

def list_shift_notes():
    return ShiftNote.objects.all()

def get_shift_note(shift_note_id: int):
    return ShiftNote.objects.filter(id=shift_note_id).first()

def create_shift_note(data: dict, user_id: int = None):
    create_log("Shift note created", user_id)
    return ShiftNote.objects.create(
        content=data["content"],
        shift_type=data["shift_type"],
        date=data.get("date"),
        order_id=data["order_id"]
    )

def update_shift_note(shift_note_id: int, data: dict, user_id: int = None):
    shift_note = ShiftNote.objects.filter(id=shift_note_id).first()
    if not shift_note:
        return None

    for field, value in data.items():
        setattr(shift_note, field, value)

    shift_note.save()
    create_log("Shift note updated", user_id)
    return shift_note

def delete_shift_note(shift_note_id: int, user_id: int = None):
    shift_note = ShiftNote.objects.filter(id=shift_note_id).first()
    if not shift_note:
        return False
    shift_note.delete()
    create_log("Shift note deleted", user_id)
    return True