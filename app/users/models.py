from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
  class UserStatus(models.TextChoices):
    CREATED = 'CREATED', 'Created'
    VERIFIED = 'VERIFIED', 'Verified'
    DELETED = 'DELETED', 'Deleted'
    BANNED = 'BANNED', 'Banned'
    
  profile_description = models.TextField(null=True, blank=True)
  email = models.EmailField(unique=True, blank=False, null=False)
  status = models.CharField(max_length=10, choices=UserStatus.choices, default=UserStatus.CREATED)
  first_name = None   # removes the first and last name from database (overrides default value for these fields)
  last_name = None
  location = models.TextField(max_length=20, blank=True, null=True)
  last_login = models.DateTimeField(null=True)
  created_at = models.DateTimeField(default=timezone.now)
  last_edited_at = models.DateTimeField(default=timezone.now)
  
  def __str__(self):
    return self.username