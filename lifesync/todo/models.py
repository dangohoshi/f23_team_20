from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ToDoItem(models.Model):
    """
    This is the model for a to-do item
    """
    users = models.ManyToManyField(User)
    deadline = models.DateTimeField()
    item = models.CharField(max_length=255)
    status = models.BooleanField(default=False)


class ToDoList(models.Model):
    """
    This is the model for a to-do list
    """
    users = models.ManyToManyField(User)
    items = models.ManyToManyField(ToDoItem)
    name = models.CharField(max_length=255, default='My To-Do List')
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, default='')
    key = models.BinaryField()
