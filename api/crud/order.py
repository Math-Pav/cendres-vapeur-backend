from apps.models import Order
from django.contrib.auth.models import User

def list_orders():
    return Order.objects.select_related("user").all()

def get_order(order_id: int):
    return Order.objects.filter(id=order_id).first()

def create_order(data: dict):
    user = User.objects.get(id=data["user_id"])
    return Order.objects.create(
        status=data["status"],
        total_amount=data["total_amount"],
        invoice_file=data.get("invoice_file"),
        user=user,
        created_at=data.get("created_at")
    )

def update_order(order_id: int, data: dict):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return None

    for field, value in data.items():
        if field == "user_id":
            order.user_id = value
        else:
            setattr(order, field, value)

    order.save()
    return order

def delete_order(order_id: int):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return False
    order.delete()
    return True
