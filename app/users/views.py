from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm

User = get_user_model()

def register(request):
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.is_active = False
      user.save()
      
      uid = urlsafe_base64_encode(force_bytes(user.pk))
      token = default_token_generator.make_token(user)
      
      current_site = request.get_host()
      activation_link = f"http://{current_site}/users/activate/{uid}/{token}/"
      
      subject = 'Activate your account on the LARP Marketplace!'
      message = f"Hello {user.username},\n\nTo complete your registration, click following link:\n{activation_link}"
      
      send_mail(subject, message, 'noreply@muj-marketplace.cz', [user.email])
      
      messages.info(request, 'First step of registration successful. Check your email inbox for confirmation link. ')
      return redirect('login')
  else:
    form = CustomUserCreationForm()
      
  return render(request, 'users/register.html', {'form': form})

def activate_account(request, uidb64, token):
  try:
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
  except (TypeError, ValueError, OverflowError, User.DoesNotExist):
    user = None

  if user is not None and default_token_generator.check_token(user, token):
    user.is_active = True
    user.status = User.UserStatus.VERIFIED
    user.save()
    messages.success(request, 'Your account was created successfully. You can log in now. ')
    return redirect('login')
  else:
    messages.error(request, 'The activation link in invalid or expired.')
    return render(request, 'users/activation_failed.html')
  
@login_required
def edit_profile(request):
  if request.method == 'POST':
    form = UserProfileForm(request.POST, instance=request.user)
    if form.is_valid():
      form.save()
      messages.success(request, 'Your profile was successfully updatesd..')
      return redirect('edit_profile')
  else:
    form = UserProfileForm(instance=request.user)
      
  return render(request, 'users/edit_profile.html', {'form': form})

def view_profile(request, id):
  user = get_object_or_404(User, id = id)
  return render(request, "users/view_profile.html", {'user' : user})
