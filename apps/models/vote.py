from django.db import models

class Vote(models.Model):
    user_id = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    