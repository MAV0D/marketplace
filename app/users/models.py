from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
  class Status(models.TextChoices):
    CREATED = 'CREATED', 'Created'
    VERIFIED = 'VERIFIED', 'Verified'
    DELETED = 'DELETED', 'Deleted'
    BANNED = 'BANNED', 'Banned'
    
  bio = models.TextField(null=True, blank=True)
  status = models.CharField(max_length=10, choices=Status.choices)
  first_name = None
  last_name = None
  