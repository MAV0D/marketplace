from django.shortcuts import render, get_object_or_404, redirect
from .models import Listing
from .forms import NewListingForm
from images.models import ListingImage

# Create your views here.
def index(request):
  listings = Listing.objects.all()
  return render(request, 'listings/index.html', {'listings' : listings})

def detail(request, id):
  listing = get_object_or_404(Listing, id = id)
  return render(request, "listings/detail_view.html", {'listing' : listing})

def create_listing(request):
  if request.method == 'POST':
    form = NewListingForm(request.POST, request.FILES)
    if form.is_valid():
      listing = form.save(commit=False)
      listing.seller = request.user
      listing.save()

      # Tady je ten trik: 'images' je název pole z tvého ListingForm
      files = request.FILES.getlist('images')
      for f in files:
        ListingImage.objects.create(
          listing=listing,
          file=f,
          is_main=False
        )
      
      return redirect('listing_detail', id=listing.id)

  else:
    form = NewListingForm()
    
  return render(request, 'listings/listing_form.html', {'form': form})