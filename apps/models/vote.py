from django.db import models

class Vote(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    