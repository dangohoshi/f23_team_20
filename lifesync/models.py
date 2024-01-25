from django.db import models
from django.contrib.auth.models import User
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    text_color = models.CharField(max_length=20, default='rgb(186, 75, 47)')
    navbar_color = models.CharField(max_length=20, default='rgb(255, 219, 213)')
