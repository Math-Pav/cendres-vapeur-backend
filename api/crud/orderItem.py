from apps.models import OrderItem
from apps.classes.log import create_log

def list_order_items():
    return OrderItem.objects.select_related("order", "product").all()

def get_order_item(order_item_id: int):
    return OrderItem.objects.filter(id=order_item_id).first()

def create_order_item(data: dict, user_id: int = None):
    create_log("Order item created", user_id)
    return OrderItem.objects.create(
        order_id=data["order_id"],
        product_id=data["product_id"],
        quantity=data["quantity"],
        unit_price_frozen=data["unit_price_frozen"]
    )

def update_order_item(order_item_id: int, data: dict, user_id: int = None):
    item = OrderItem.objects.filter(id=order_item_id).first()
    if not item:
        return None

    for field, value in data.items():
        setattr(item, field, value)

    item.save()
    create_log("Order item updated", user_id)
    return item

def delete_order_item(order_item_id: int, user_id: int = None):
    item = OrderItem.objects.filter(id=order_item_id).first()
    if not item:
        return False
    item.delete()
    create_log("Order item deleted", user_id)
    return True