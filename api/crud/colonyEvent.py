from apps.classes.log import create_log
from apps.models import ColonyEvent

def list_colony_events():
    return ColonyEvent.objects.all()

def get_colony_event(event_id: int):
    return ColonyEvent.objects.filter(id=event_id).first()

def create_colony_event(data: dict):
    create_log("Colony event created", data["title"])
    return ColonyEvent.objects.create(
        title=data["title"],
        date=data["date"],
        severity=data["severity"]
    )

def update_colony_event(event_id: int, data: dict):
    event = ColonyEvent.objects.filter(id=event_id).first()
    if not event:
        return None

    for field, value in data.items():
        setattr(event, field, value)

    event.save()
    create_log("Colony event updated", data["title"])
    return event

def delete_colony_event(event_id: int):
    event = ColonyEvent.objects.filter(id=event_id).first()
    if not event:
        return False
    event.delete()
    create_log("Colony event deleted", data["title"])
    return True