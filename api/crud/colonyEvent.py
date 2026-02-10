from apps.classes.log import create_log
from apps.models import ColonyEvent

def list_colony_events():
    return ColonyEvent.objects.all()

def get_colony_event(event_id: int):
    return ColonyEvent.objects.filter(id=event_id).first()

def create_colony_event(data: dict, user_id: int = None):
    create_log("Colony event created", user_id)
    return ColonyEvent.objects.create(
        title=data["title"],
        date=data["date"],
        severity=data["severity"]
    )

def update_colony_event(event_id: int, data: dict, user_id: int = None):
    event = ColonyEvent.objects.filter(id=event_id).first()
    if not event:
        return None

    for field, value in data.items():
        setattr(event, field, value)

    event.save()
    create_log("Colony event updated", user_id)
    return event

def delete_colony_event(event_id: int, user_id: int = None):
    event = ColonyEvent.objects.filter(id=event_id).first()
    if not event:
        return False
    event.delete()
    create_log("Colony event deleted", user_id)
    return True