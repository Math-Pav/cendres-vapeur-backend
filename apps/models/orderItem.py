from django.db import models

class OrderItem(models.Model):
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price_frozen = models.DecimalField(max_digits=10, decimal_places=2)