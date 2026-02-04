from django.db import models

class ShiftNote(models.Model):
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    shift_type = models.EnumField(choices=['MORNING', 'EVENING'])
    content = models.TextField()
