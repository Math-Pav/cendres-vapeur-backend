from django.db import models

class ShiftNote(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    date = models.DateField()
    shift_type = models.CharField(max_length=10, choices=[('MORNING', 'Morning'), ('EVENING', 'Evening')])
    content = models.TextField()
    
