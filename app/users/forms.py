from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from images.models import ProfilePicture

class CustomUserCreationForm(UserCreationForm):
  class Meta(UserCreationForm.Meta):
    model = get_user_model()
    fields = UserCreationForm.Meta.fields + ('email', 'location')
      
  def clean_email(self):
    email = self.cleaned_data.get('email')
    if get_user_model().objects.filter(email=email).exists():
      raise forms.ValidationError("User with this email already exists.")
    return email

class ProfilePictureForm(forms.ModelForm):
  class Meta:
    model = ProfilePicture
    fields = ('file',)
    widgets = {
      'file': forms.FileInput(attrs={'accept': 'image/*'})
    }
  
class UserProfileForm(forms.ModelForm):
  class Meta:
    model = get_user_model()
    fields = ('email', 'profile_description', 'location')
    
class UserProfileForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    self.user = kwargs.get('instance', None)
    super().__init__(*args, **kwargs)
  
  class Meta:
    model = get_user_model()
    fields = ('email', 'profile_description', 'location')
    
  def clean_current_password(self):
    current_password = self.cleaned_data.get('current_password')
    
    # Ověříme, zda zadané heslo odpovídá zašifrovanému heslu v databázi
    if self.user and not check_password(current_password, self.user.password):
      raise forms.ValidationError("Your current password is  incorrect.")
    
    return current_password
    
  def clean_email(self):
    email = self.cleaned_data.get('email')
    User = get_user_model()
    
    # If email hasn't changed, don't validate
    if self.instance and self.instance.email == email:
      return email
    
    # If email has changed, check if it's already taken
    if User.objects.filter(email=email).exists():
      raise forms.ValidationError("This email is already in use.")
    
    return email