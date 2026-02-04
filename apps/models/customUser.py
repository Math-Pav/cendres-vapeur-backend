from django.db import models

class CustomUser (models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.enumField(choices=['EDITOR', 'ADMIN', 'USER', 'INVITE'], default='USER')
    avatar_url = models.URLField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
    