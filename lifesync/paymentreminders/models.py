from django.db import models
from django.contrib.auth.models import User


class ReminderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_title = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    due_date = models.DateTimeField()
