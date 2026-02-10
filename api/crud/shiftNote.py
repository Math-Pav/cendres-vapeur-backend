from apps.models import ShiftNote

def list_shift_notes():
    return ShiftNote.objects.all()

def get_shift_note(shift_note_id: int):
    return ShiftNote.objects.filter(id=shift_note_id).first()

def create_shift_note(data: dict):
    create_log("Shift note created", data["shift_type"])
    return ShiftNote.objects.create(
        content=data["content"],
        shift_type=data["shift_type"],
        date=data.get("date"),
        order_id=data["order_id"]
    )

def update_shift_note(shift_note_id: int, data: dict):
    shift_note = ShiftNote.objects.filter(id=shift_note_id).first()
    if not shift_note:
        return None

    for field, value in data.items():
        setattr(shift_note, field, value)

    shift_note.save()
    create_log("Shift note updated", shift_note.shift_type)
    return shift_note

def delete_shift_note(shift_note_id: int):
    shift_note = ShiftNote.objects.filter(id=shift_note_id).first()
    if not shift_note:
        return False
    shift_note.delete()
    create_log("Shift note deleted", shift_note.shift_type)
    return True