from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
  class Meta(UserCreationForm.Meta):
    model = get_user_model()
    fields = UserCreationForm.Meta.fields + ('email', 'location')
      
  def clean_email(self):
    email = self.cleaned_data.get('email')
    if get_user_model().objects.filter(email=email).exists():
      raise forms.ValidationError("User with this email already exists.")
    return email
  
class UserProfileForm(forms.ModelForm):
  class Meta:
    model = get_user_model()
    fields = ('email', 'profile_description')
