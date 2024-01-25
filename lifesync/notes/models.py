from django.contrib.auth.models import User
from django.db import models


class Note(models.Model):
    users = models.ManyToManyField(User)
    created_time = models.DateTimeField()
    latest_update_time = models.DateTimeField()
    name = models.CharField(max_length=255)
    content = models.CharField(max_length=2048)
    description = models.CharField(max_length=255, default='')
    key = models.BinaryField()


class Category(models.Model):
    users = models.ManyToManyField(User)
    notes = models.ManyToManyField(Note)
    name = models.CharField(max_length=255, default='My Notes')
    created_time = models.DateTimeField()
    description = models.CharField(max_length=255, default='')
