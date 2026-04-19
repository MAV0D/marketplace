from django.contrib import admin
from listings.models import EquipmentType, Listing
from users.models import User
from images.models import ProfilePicture, ListingImage

class ProfilePictureInline(admin.TabularInline):
  model = ProfilePicture
  extra = 1
  max_num = 1 # Uživatel má jen jednu profilovku
  
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  inlines = [ProfilePictureInline]
  
class ListingImageInline(admin.TabularInline):
  model = ListingImage
  extra = 3
  
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
  inlines = [ListingImageInline]
  
  
admin.site.register(EquipmentType)