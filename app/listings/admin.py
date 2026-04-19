from django.contrib import admin
from listings.models import EquipmentType, Listing, ListingAttribute, FilterAttribute, FilterValue
from users.models import User
from images.models import ProfilePicture, ListingImage

class ProfilePictureInline(admin.TabularInline):
  model = ProfilePicture
  extra = 1
  max_num = 1
  
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  inlines = [ProfilePictureInline]
  
class ListingImageInline(admin.TabularInline):
  model = ListingImage
  extra = 1

class ListingAttributeInline(admin.TabularInline):
  model = ListingAttribute
  extra = 1
  
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
  inlines = [ListingImageInline, ListingAttributeInline]
  
  
admin.site.register(EquipmentType)

class FilterValueInline(admin.TabularInline):
  model = FilterValue
  extra = 3
  
@admin.register(FilterAttribute)
class FilterAttributeAdmin(admin.ModelAdmin):
  list_display = ('name', 'is_numeric')
  inlines = [FilterValueInline]