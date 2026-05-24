from django.db import models
from listings.models import Listing
from users.models import User

class Transaction(models.Model):
  class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    DONE = 'DONE', 'Done'
    RATED = 'RATED', 'Rated'
    CANCELLED = 'CANCELLED', 'Cancelled'
    
  class Type(models.TextChoices):
    RENTAL = 'RENTAL', 'Rental'
    SALE = 'SALE', 'Sale'
    
  date = models.DateTimeField(auto_now_add=True)
  buyer_rating = models.IntegerField(null=True, blank=True)
  seller_rating = models.IntegerField(null=True, blank=True)
  status = models.CharField(max_length=10, choices=Status, default=Status.PENDING)
  type = models.CharField(max_length=10, choices=Type)
  start_date = models.DateField(blank=True, null=True)
  end_date = models.DateField(blank=True, null=True)
  listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
  buyer = models.ForeignKey(User, on_delete=models.CASCADE)
  
  def __str__(self):
    return f"{self.listing.name} - {self.type}"


class Sale(Transaction):
  class Meta:
    proxy = True
      
  def save(self, *args, **kwargs):
    self.type = Transaction.Type.SALE
    super().save(*args, **kwargs)
    
class Rental(Transaction):
  class Meta:
    proxy = True
      
  def save(self, *args, **kwargs):
    self.type = Transaction.Type.RENTAL
    super().save(*args, **kwargs)