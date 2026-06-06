from django.urls import path
from . import views

urlpatterns = [
  path('<int:id>/', views.detail, name='listing_detail'),
  path('create-listing', views.create_listing, name='create_listing'),
  path('edit/<int:id>/', views.edit_listing, name='edit_listing'),
  path('delete/<int:id>/', views.delete_listing, name='delete_listing'),
  path('upload-listing-image/<int:listing_id>/', views.upload_listing_images, name='upload_listing_images'),
  path('delete-listing-image/<int:id>/', views.delete_listing_image, name='delete_listing_image'),
  path('image/<int:id>/set-main/', views.set_main_image, name='set_main_image'),
  path('image/<int:id>/move/<str:direction>/', views.move_image, name='move_image'),
  path('get-attributes/', views.get_attributes_for_category, name='get_attributes_for_category'),
]