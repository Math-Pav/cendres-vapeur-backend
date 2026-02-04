from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/images/')
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    stock = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    popularity_score = models.FloatField()

    def __str__(self):
        return self.name