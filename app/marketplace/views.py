from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.db.models import Q
from listings.models import Listing, EquipmentType

def index(request):
  # Get sorting parameter from URL, defaulting to newest listings first
  sort_by = request.GET.get('order_by', '-created_at')
  
  # Map human-readable dropdown options securely to model database fields
  allowed_sorting = {
    '-created_at': '-created_at',       # Newest First
    'created_at': 'created_at',         # Oldest First
    'selling_price': 'selling_price',   # Price: Low to High
    '-selling_price': '-selling_price', # Price: High to Low
    'name': 'name'                      # Alphabetical
  }
  
  # Fallback to default if an unexpected sorting key is passed
  order_field = allowed_sorting.get(sort_by, '-created_at')

  # Base Queryset with ordering injected directly
  listings = Listing.objects.filter(status=Listing.Status.VISIBLE).prefetch_related('images').order_by(order_field)
  categories = EquipmentType.objects.filter(parent=None).prefetch_related('children')
  
  # Handle Category Filtering
  selected_slug = request.GET.get('category')
  selected_category = None
  if selected_slug:
    try:
      selected_category = EquipmentType.objects.get(slug=selected_slug)
      target_ids = [selected_category.id]
      
      def collect_child_ids(cat):
        for child in cat.children.all():
          target_ids.append(child.id)
          collect_child_ids(child)
          
      collect_child_ids(selected_category)
      listings = listings.filter(equipment_type_id__in=target_ids)
    except EquipmentType.DoesNotExist:
      pass

  # Handle Text Search Matching
  search_query = request.GET.get('q')
  if search_query:
    search_query = search_query.strip()
    listings = listings.filter(
      Q(name__icontains=search_query) | 
      Q(description__icontains=search_query)
    )

  # PAGINATION ENGINE: Split total listings into chunks of 20 items per page
  paginator = Paginator(listings, 20)
  page_number = request.GET.get('page', 1)
  
  try:
    page_obj = paginator.page(page_number)
  except PageNotAnInteger:
    page_obj = paginator.page(1)
  except EmptyPage:
    page_obj = paginator.page(paginator.num_pages)

  context = {
    'listings': page_obj,               # Swapped out raw queryset for page object chunk
    'categories': categories,
    'selected_category': selected_category,
    'current_order': sort_by,           # Used to set 'selected' state in HTML template dropdown
  }
  return render(request, 'index.html', context)