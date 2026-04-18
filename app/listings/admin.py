from django.contrib import admin
from listings.models import EquipmentType, Listing
from users.models import User

admin.site.register(User)
admin.site.register(EquipmentType)
admin.site.register(Listing)