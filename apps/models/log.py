from django.db import models


class Log(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

