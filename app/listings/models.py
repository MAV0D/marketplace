from django.db import models
from users.models import User

# Create your models here.
class EquipmentType(models.Model):
  slug = models.SlugField(max_length=70)
  name = models.CharField(max_length=20)
  description = models.TextField()
  parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
  filter_options = models.ManyToManyField('FilterAttribute')
  
  def __str__(self):
    return self.name
  
  def get_full_path(self):
    if self.parent:
        return f"{self.parent.get_full_path()}/{self.slug}"
    return f"/{self.slug}"


class Listing(models.Model):
  class Condition(models.TextChoices):
    NEW = 'NEW', 'New'
    UNPACKED = 'UNPACKED', 'Unpacked'
    USED = 'USED', 'Used'
    DAMAGED = 'DAMAGED', 'Damaged'
    
  class Status(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    VISIBLE = 'VISIBLE', 'Visible'
    HIDDEN = 'HIDDEN', 'Hidden'
    SOLD = 'SOLD', 'Sold'
    ARCHIVED = 'ARCHIVED', 'Archived'
  
  name = models.CharField(max_length=20)
  description = models.TextField(null=True)
  for_rent = models.BooleanField()
  for_sale = models.BooleanField()
  selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  renting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  condition = models.CharField(max_length=10, choices=Condition.choices, null=True)
  views_count = models.IntegerField(default=0)
  status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
  created_at = models.DateTimeField(auto_now_add=True)
  last_edited_at = models.DateTimeField(auto_now=True)
  seller = models.ForeignKey(User, on_delete=models.CASCADE)
  equipment_type = models.ForeignKey('EquipmentType', on_delete=models.PROTECT, null=True)
  
  def archive_listing(self):
    self.status = self.Status.ARCHIVED
    
  def calculatePrice(self, days):
    return self.renting_price * days
    
  def __str__(self):
    return self.name
  
  @property
  def main_image(self):
    """Vrátí hlavní obrázek inzerátu, případně první dostupný, nebo None"""
    # 1. Pokusíme se najít obrázek s příznakem is_main
    main_img = self.images.filter(is_main=True).first()
    if main_img:
      return main_img
      
    # 2. Záloha: Pokud z nějakého důvodu is_main chybí, vezmeme první obrázek v pořadí
    return self.images.first()
  
class FilterAttribute(models.Model):
  name = models.CharField(max_length=20)
  is_numeric = models.BooleanField(default=False)
  
  def __str__(self):
    return self.name
  
class FilterValue(models.Model):
  value = models.CharField(max_length=20)
  numeric_value = models.FloatField(null=True, blank=True)
  attribute = models.ForeignKey('FilterAttribute', on_delete=models.CASCADE)
  
  def __str__(self):
    return self.value
  
class ListingAttribute(models.Model):
  listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='attributes')
  value = models.ForeignKey('FilterValue', on_delete=models.CASCADE)
  
  def __str__(self):
    return f"{str(self.value.attribute)} - {self.value}"
