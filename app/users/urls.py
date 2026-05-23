from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
  path('register/', views.register, name='register'),
  path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
  path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate_account'),
  path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
  path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
  path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
        name='password_reset_confirm'),
  path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
  path('edit/', views.edit_profile, name='edit_profile'),
  path('password-change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html'), name='password_change'),
  path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
  path('profile/<int:id>/', views.view_profile, name='view_profile'),
  path('delete-profile/<int:id>/', views.delete_profile, name='delete_profile'),
  path('profile/edit/delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
  path('profile/edit/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),
]