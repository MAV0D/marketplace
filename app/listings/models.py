from django.db import models
import datetime
from users.models import User

# Create your models here.
class EquipmentType(models.Model):
  slug = models.SlugField(max_length=70)
  name = models.CharField(max_length=20)
  description = models.TextField()
  parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
  
  def __str__(self):
    return self.name
  
  def get_full_path(self):
    return f"{self.parent.get_full_path() if self.parent != None else ""}/{self.slug}"


class Listing(models.Model):
  class Condition(models.TextChoices):
    NEW = 'NEW', 'New'
    UNPACKED = 'UNPACKED', 'Unpacked'
    USED = 'USED', 'Used'
    DAMAGED = 'DAMAGED', 'Damaged'
    
  class Status(models.TextChoices):
    VISIBLE = 'VISIBLE', 'Visible'
    HIDDEN = 'HIDDEN', 'Hidden'
    SOLD = 'SOLD', 'Sold'
    ARCHIVED = 'ARCHIVED', 'Archived'
  
  name = models.CharField(max_length=20)
  description = models.TextField()
  for_rent = models.BooleanField()
  for_sale = models.BooleanField()
  selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  renting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  condition = models.CharField(max_length=10, choices=Condition.choices)
  views_count = models.IntegerField(default=0)
  status = models.CharField(max_length=10, choices=Status.choices)
  created_at = models.DateTimeField(auto_now_add=True)
  last_edited_at = models.DateTimeField(auto_now=True)
  seller = models.ForeignKey(User, on_delete=models.CASCADE)
  equipment_type = models.ForeignKey(EquipmentType, on_delete=models.PROTECT)
  
  def archive_listing(self):
    self.status = self.Status.ARCHIVED
    
  def calculatePrice(self, days):
    return self.renting_price * days
    
  def addPicture(self, file):
    pass
  
  def __str__(self):
    return self.name