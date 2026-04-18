from django.shortcuts import render, get_object_or_404
from .models import Listing

# Create your views here.
def index(request):
  listings = Listing.objects.all()
  return render(request, 'listings/index.html', {'listings' : listings})

def detail(request, id):
  data = get_object_or_404(Listing, id = id)
  return render(request, "listings/detail_view.html", {'data' : data})