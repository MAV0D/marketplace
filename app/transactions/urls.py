from django.urls import path
from . import views

urlpatterns = [
  path('order/<int:listing_id>/<int:order_type>/', views.order_review, name='order'),
  path('complete-transaction/<str:uidb64>/<str:token>/', views.complete_transaction, name='complete_transaction'),
  path('status-change/<int:transaction_id>/', views.change_transaction_status, name='change_transaction_status'),
  path('rate/<int:transaction_id>/<int:rating_value>/', views.rate_transaction, name='rate_transaction'),
]