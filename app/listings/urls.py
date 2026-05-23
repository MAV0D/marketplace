from django.urls import path
from .views import detail, create_listing, edit_listing, delete_listing

urlpatterns = [
  path('<int:id>/', detail, name='listing_detail'),
  path('create-listing', create_listing, name='create_listing'),
  path('edit/<int:id>/', edit_listing, name='edit_listing'),
  path('delete/<int:id>/', delete_listing, name='delete_listing'),
]