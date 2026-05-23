from django.shortcuts import render
from listings.models import Listing


def index(request):
  listings = Listing.objects.all()
  return render(request, 'index.html', {'listings' : listings})