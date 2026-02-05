from django.db import models

class ColonyEvent(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    severity = models.CharField(max_length=10, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')])
    