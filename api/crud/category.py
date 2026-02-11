from apps.classes.log import create_log
from apps.models import Category
from datetime import datetime

def list_categories():
    return Category.objects.all()

def get_category(category_id: int):
    return Category.objects.filter(id=category_id).first()

def create_category(data: dict, user_id: int = None):
    create_log("Category created", user_id)
    return Category.objects.create(
        name=data["name"],
        description=data.get("description"),
        created_at=data.get("created_at")
    )

def update_category(category_id: int, data: dict, user_id: int = None):
    category = Category.objects.filter(id=category_id).first()
    if not category:
        return None

    for field, value in data.items():
        setattr(category, field, value)

    category.save()
    create_log("Category updated", user_id)
    return category

def delete_category(category_id: int, user_id: int = None):
    category = Category.objects.filter(id=category_id).first()
    if not category:
        return False
    category.delete()
    create_log("Category deleted", user_id)
    return True