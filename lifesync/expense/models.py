from django.db import models
from django.contrib.auth.models import User


class ExpenseItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField()
    expense_title = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255)
