from django.db import models

class Order(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('PENDING', 'Pending'), ('SHIPPED', 'Shipped'), ('PAID', 'Paid')], default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    invoice_file = models.FileField(upload_to='orders/invoices/', blank=True, null=True)
    