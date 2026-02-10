from apps.models import CustomUser
from django.contrib.auth.hashers import make_password
from apps.classes.log import create_log
from apps.classes.log import create_log

def list_users():
    return CustomUser.objects.all()

def get_user(user_id: int):
    return CustomUser.objects.filter(id=user_id).first()

def create_user(data: dict):
    create_log("User created", data["username"])
    return CustomUser.objects.create(
        username=data["username"],
        email=data["email"],
        password=make_password(data["password"]),
        role="USER",
        biography=data.get("biography"),
        avatar_url=data.get("avatar_url")
    )

def update_user(user_id: int, data: dict):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return None

    for field, value in data.items():
        setattr(user, field, value)

    user.save()
    create_log("User updated", user.username)
    return user

def delete_user(user_id: int):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return False
    user.delete()
    create_log("User deleted", user.username)
    return True