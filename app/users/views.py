from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.db.models import Avg, Count
from .forms import CustomUserCreationForm, UserProfileForm, ProfilePicture, ProfilePictureForm
from listings.models import Listing
from transactions.models import Transaction

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
      if not settings.DEBUG:
        current_site += "/marketplace"
      activation_link = f"https://{current_site}/users/activate/{uid}/{token}/"
      
      send_verification_email(user.email, user.username, activation_link)
      
      messages.info(request, 'First step of registration successful. Check your email inbox for confirmation link. If the mail doesn\'t arrive, please check spam folder.')
      return redirect('login')
  else:
    form = CustomUserCreationForm()
      
  return render(request, 'users/register.html', {'form': form})

def send_verification_email(user_email, username, activation_url):
  subject = "Activate your account on the LARP Marketplace!"
  from_email = "noreply@server2.zmatlo.cz"
  to = [user_email]

  context = {
    'username': username,
    'activation_url': activation_url,
  }

  html_content = render_to_string('emails/activation_email.html', context)
  text_content = strip_tags(html_content)

  msg = EmailMultiAlternatives(subject, text_content, from_email, to)
  msg.attach_alternative(html_content, "text/html")
  msg.send()

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
  shown_user = get_object_or_404(User, id = id)
  listings = Listing.objects.filter(seller=shown_user, status=Listing.Status.VISIBLE)
  
  buyer_stats = Transaction.objects.filter(
    buyer=shown_user, 
    buyer_rating__isnull=False
  ).aggregate(avg=Avg('buyer_rating'), count=Count('buyer_rating'))
  
  seller_stats = Transaction.objects.filter(
    listing__seller=shown_user, 
    seller_rating__isnull=False
  ).aggregate(avg=Avg('seller_rating'), count=Count('seller_rating'))
  
  total_rating_sum = 0
  total_rating_count = 0
  
  if buyer_stats['avg'] and buyer_stats['count']:
    total_rating_sum += buyer_stats['avg'] * buyer_stats['count']
    total_rating_count += buyer_stats['count']
    
  if seller_stats['avg'] and seller_stats['count']:
    total_rating_sum += seller_stats['avg'] * seller_stats['count']
    total_rating_count += seller_stats['count']
    
  if total_rating_count > 0:
    average_rating = round(total_rating_sum / total_rating_count, 1)
  else:
    average_rating = None
  
  context = {
    'shown_user' : shown_user,
    'listings':listings,
    'average_rating': average_rating,
    'rating_count': total_rating_count,
  }
  
  return render(request, "users/view_profile.html", context)


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