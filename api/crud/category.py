from apps.models import Category
from datetime import datetime


def list_categories():
    return Category.objects.all()

def get_category(category_id: int):
    return Category.objects.filter(id=category_id).first()

def create_category(data: dict):
    create_log("Category created", data["name"])
    return Category.objects.create(
        name=data["name"],
        description=data.get("description"),
        created_at=data.get("created_at")
    )

def update_category(category_id: int, data: dict):
    category = Category.objects.filter(id=category_id).first()
    if not category:
        return None

    for field, value in data.items():
        setattr(category, field, value)

    category.save()
    create_log("Category updated", data["name"])
    return category

def delete_category(category_id: int):
    category = Category.objects.filter(id=category_id).first()
    if not category:
        return False
    category.delete()
    create_log("Category deleted", data["name"])
    return True

