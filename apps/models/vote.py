from django.db import models

class Vote(models.Model):
    user = models.ForeignKey('apps.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey('apps.Product', related_name='votes', on_delete=models.CASCADE)
    
    
    comment = models.TextField(blank=True, null=True) 
    
    note = models.IntegerField(default=0)
    like = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"Vote sur {self.product_id} par utilisateur {self.user_id}"