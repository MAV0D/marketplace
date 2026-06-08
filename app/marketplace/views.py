from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from listings.models import Listing, EquipmentType, FilterAttribute

def index(request):
  sort_by = request.GET.get('order_by', '-created_at')
  
  allowed_sorting = {
    '-created_at': '-created_at',       
    'created_at': 'created_at',         
    'selling_price': 'selling_price',   
    '-selling_price': '-selling_price', 
    'name': 'name'                      
  }
  
  order_field = allowed_sorting.get(sort_by, '-created_at')

  listings = Listing.objects.filter(status=Listing.Status.VISIBLE).prefetch_related('images').order_by(order_field)
  categories = EquipmentType.objects.filter(parent=None).prefetch_related('children')
  
  selected_slug = request.GET.get('category')
  selected_category = None
  available_filters = []
  
  active_numeric_filters = {} 

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
      
      available_filters = FilterAttribute.objects.filter(
          equipmenttype__in=target_ids
      ).distinct().prefetch_related('filtervalue_set')
      
      chosen_filter_ids = request.GET.getlist('filter_val')
      if chosen_filter_ids:
        for val_id in chosen_filter_ids:
          listings = listings.filter(attributes__value_id=val_id).distinct()

      for attr in available_filters:
        if attr.is_numeric:
          min_key = f'min_attr_{attr.id}'
          max_key = f'max_attr_{attr.id}'
          
          min_val = request.GET.get(min_key)
          max_val = request.GET.get(max_key)
          
          active_numeric_filters[attr.id] = {
              'min': min_val if min_val else '',
              'max': max_val if max_val else ''
          }
          
          if min_val or max_val:
            attr_q = Q(attributes__value__attribute=attr)
            if min_val:
              attr_q &= Q(attributes__value__numeric_value__gte=float(min_val))
            if max_val:
              attr_q &= Q(attributes__value__numeric_value__lte=float(max_val))
            
            listings = listings.filter(attr_q).distinct()

    except EquipmentType.DoesNotExist:
      pass

  search_query = request.GET.get('q')
  if search_query:
    search_query = search_query.strip()
    listings = listings.filter(
      Q(name__icontains=search_query) | 
      Q(description__icontains=search_query)
    )

  paginator = Paginator(listings, 8)
  page_number = request.GET.get('page', 1)
  
  try:
    page_obj = paginator.page(page_number)
  except PageNotAnInteger:
    page_obj = paginator.page(1)
  except EmptyPage:
    page_obj = paginator.page(paginator.num_pages)

  context = {
    'listings': page_obj,
    'categories': categories,
    'selected_category': selected_category,
    'current_order': sort_by,
    'available_filters': available_filters,
    'active_numeric_filters': active_numeric_filters,
  }
  return render(request, 'index.html', context)

@require_POST
def accept_cookies(request):
  response = HttpResponse("")
  response.set_cookie('cookies_accepted', 'true', max_age=31536000) # one year
  return response