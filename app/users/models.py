from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
  class UserStatus(models.TextChoices):
    CREATED = 'CREATED', 'Created'
    VERIFIED = 'VERIFIED', 'Verified'
    DELETED = 'DELETED', 'Deleted'
    BANNED = 'BANNED', 'Banned'
    
  profile_description = models.TextField(null=True, blank=True)
  status = models.CharField(max_length=10, choices=UserStatus.choices)
  first_name = None
  last_name = None
  location = models.TextField(max_length=20, blank=True, null=True)
  last_login = models.DateTimeField(null=True)
  created_at = models.DateTimeField()
  last_edited_at = models.DateTimeField()
  
  def __str__(self):
    return self.username