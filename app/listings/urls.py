from django.urls import path
from .views import index, detail, create_listing

urlpatterns = [
  path('', index, name='index'),
  path('listing/<int:id>/', detail, name='listing_detail'),
  path('listing/create_listing', create_listing, name='create_listing'),
]