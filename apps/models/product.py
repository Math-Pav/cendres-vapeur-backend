from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/images/')
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    stock = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    popularity_score = models.FloatField()
    
    view_count = models.IntegerField(default=0) 
    purchase_count = models.IntegerField(default=0)  
    base_stock = models.IntegerField(default=0)
    price_change_percentage = models.FloatField(default=0.0)
    last_price_update = models.DateTimeField(default=timezone.now)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    