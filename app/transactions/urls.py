from django.urls import path
from . import views

urlpatterns = [
  path('order/<int:listing_id>/<int:order_type>/', views.order_review, name='order'),
  path('dashboard/', views.transaction_dashboard, name='transaction_dashboard'),
  path('status/<int:transaction_id>/', views.change_transaction_status, name='change_transaction_status'),
  path('rate/<int:transaction_id>/', views.rate_transaction, name='rate_transaction'),
]