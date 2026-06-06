from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    favourite_genre = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username
    


