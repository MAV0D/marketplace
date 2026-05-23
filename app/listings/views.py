from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponse
from .models import Listing
from .forms import ListingForm
from images.models import ListingImage

def detail(request, id):
  listing = get_object_or_404(Listing, id = id)
  return render(request, "listings/detail_view.html", {'listing' : listing})

@login_required
def create_listing(request):
  listing, created = Listing.objects.get_or_create(
      seller=request.user,
      status=Listing.Status.DRAFT,
      defaults={
        'name': '',
        'description': '',
        'for_rent' : False,
        'for_sale' : False,
        'seller' : request.user,
      }
    )
  
  if request.method == 'POST':
    form = ListingForm(request.POST, request.FILES, instance=listing)
    if form.is_valid():
      listing = form.save(commit=False)
      listing.seller = request.user
      listing.status = Listing.Status.VISIBLE
      listing.save()
      
      return redirect('listing_detail', id=listing.id)

  else:
    form = ListingForm(instance=listing)
    
  return render(request, 'listings/listing_form.html', {'form': form, 'listing' : listing})

def edit_listing(request, id):
  listing = get_object_or_404(Listing, id=id)
  
  if listing.seller != request.user:
      raise PermissionDenied
    
  if request.method == "POST":
    form = ListingForm(request.POST, request.FILES, instance=listing)
    if form.is_valid():
      form.save()
      
      image_ids_to_delete = request.POST.getlist('delete_images')
      if image_ids_to_delete:
        images_to_del = ListingImage.objects.filter(id__in=image_ids_to_delete, listing=listing)
        images_to_del.delete()
      
      files = request.FILES.getlist('images')
      for f in files:
        ListingImage.objects.create(
          listing=listing,
          file=f,
          is_main=False
        )
      
      return redirect('listing_detail', id=listing.id)
  else:
    form = ListingForm(instance=listing)
    
  return render(request, 'listings/listing_form.html', {
    'form': form, 
    "listing":listing
  })


@login_required
@require_POST
def delete_listing(request, id):
  listing = get_object_or_404(Listing, id=id)
  
  if listing.seller != request.user:
    raise PermissionDenied
  
  listing.delete()
  
  messages.success(request, "Inzerát byl úspěšně smazán.")
  return redirect('index')

@login_required
@require_POST
def delete_listing_image(request, id):

  try:
    image = get_object_or_404(ListingImage, id=id, listing__seller=request.user)
    image.delete()
  except ListingImage.DoesNotExist:
    pass
  
  return HttpResponse("")

@login_required
@require_POST
def upload_listing_images(request, listing_id):
  listing = get_object_or_404(Listing, id=listing_id, seller=request.user)
  files = request.FILES.getlist('images')
  
  if files:
    last_image = listing.images.order_by('-position').first()
    current_position = last_image.position if last_image else 0
    
    for f in files:
      
      current_position += 1
      
      ListingImage.objects.create(
        listing=listing,
        file=f,
        position=current_position,
        is_main=(current_position == 1)
      )
  
  return render(request, 'listings/partials/listing_images_snippet.html', {'listing': listing})