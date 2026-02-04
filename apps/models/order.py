from django.db import models

class Order(models.Model):
    user_id = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    status = models.EnumField(choices=['PENDING', 'SHIPPED', 'PAID'], default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    invoice_file = models.FileField(upload_to='orders/invoices/', blank=True, null=True)