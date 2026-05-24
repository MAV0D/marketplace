from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password
from .forms import CustomUserCreationForm, UserProfileForm, ProfilePicture, ProfilePictureForm
from listings.models import Listing
from images.models import ListingImage

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
  
  profile_pic_instance, created = ProfilePicture.objects.get_or_create(user=request.user)
  
  if request.method == 'POST':
    user_form = UserProfileForm(request.POST, instance=request.user)
    pic_form = ProfilePictureForm(request.POST, request.FILES, instance=profile_pic_instance)
    if 'file-clear' in request.POST:
      profile_pic_instance.delete()
      messages.success(request, 'Your profile picture was successfully removed.')
    
    if user_form.is_valid() and pic_form.is_valid():
      user_form.save()
      if 'file' in request.FILES:
        pic_form.save()
      messages.success(request, 'Your profile was successfully updated.')
      return redirect('edit_profile')

  else:
    user_form = UserProfileForm(instance=request.user)
    pic_form = ProfilePictureForm(instance=profile_pic_instance)
      
  return render(request, 'users/edit_profile.html', {'user_form': user_form, 'pic_form' : pic_form})    
    
def view_profile(request, id):
  user = get_object_or_404(User, id = id)
  listings = Listing.objects.filter(seller=user, status=Listing.Status.VISIBLE)
  return render(request, "users/view_profile.html", {'user' : user, 'listings':listings})


@login_required
@require_POST
def delete_profile(request, id):
  user = get_object_or_404(User, id=id)
  
  password = request.POST.get('delete_confirmation_password')

  
  if request.user and not check_password(password, request.user.password):
    messages.error(request, 'Wrong password. Try again.')
    return redirect('edit_profile')
  
  if user == request.user or request.user.is_staff:
    user.is_active = False
    user.status = User.UserStatus.DELETED
    user.save()
    messages.success(request, "Profile deleted successfully.")
  else:
    messages.error(request, 'You can\'t delete other accounts.')
  
  return redirect('index')

@login_required
@require_POST
def delete_profile_picture(request):
  try:
    profile_pic = ProfilePicture.objects.get(user=request.user)
    profile_pic.delete()
  except ProfilePicture.DoesNotExist:
    pass
    
  # Vytvoříme čistý prázdný formulář pro snippet
  empty_form = ProfilePictureForm()
  return render(request, 'users/partials/profile_picture_snippet.html', {'pic_form': empty_form})

@login_required
@require_POST
def upload_profile_picture(request):
  
  profile_pic_instance, created = ProfilePicture.objects.get_or_create(user=request.user)
  
  form = ProfilePictureForm(request.POST, request.FILES, instance=profile_pic_instance)
  
  if form.is_valid():
    form.save()
    profile_pic_instance.refresh_from_db()
    form = ProfilePictureForm(instance=profile_pic_instance)
  
  return render(request, 'users/partials/profile_picture_snippet.html', {'pic_form': form})