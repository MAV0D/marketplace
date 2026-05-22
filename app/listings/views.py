from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Listing
from .forms import ListingForm
from images.models import ListingImage

# Create your views here.
def index(request):
  listings = Listing.objects.all()
  return render(request, 'listings/index.html', {'listings' : listings})

def detail(request, id):
  listing = get_object_or_404(Listing, id = id)
  return render(request, "listings/detail_view.html", {'listing' : listing})

@login_required
def create_listing(request):
  if request.method == 'POST':
    form = ListingForm(request.POST, request.FILES)
    if form.is_valid():
      listing = form.save(commit=False)
      listing.seller = request.user
      listing.save()

      files = request.FILES.getlist('images')
      for f in files:
        ListingImage.objects.create(
          listing=listing,
          file=f,
          is_main=False
        )
      
      return redirect('listing_detail', id=listing.id)

  else:
    form = ListingForm()
    
  return render(request, 'listings/listing_form.html', {'form': form})

def edit_listing(request, id):
  listing = get_object_or_404(Listing, id=id)
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