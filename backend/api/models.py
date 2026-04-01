from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class List(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_lists')
    members = models.ManyToManyField(User, through='ListMember', related_name='lists')
    created_at = models.DateTimeField(auto_now_add=True)

class ListMember(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('list', 'user')

class Item(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='completed_items')
    added_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='added_items')
    created_at = models.DateTimeField(auto_now_add=True)