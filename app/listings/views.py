from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from .models import Listing, EquipmentType, ListingAttribute, FilterValue
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
      'for_rent': False,
      'for_sale': False,
      'seller': request.user,
    }
  )
  
  if request.method == 'GET' and listing.name == '':
    listing.images.all().delete()
  
  if request.method == 'POST':
    form = ListingForm(request.POST, request.FILES, instance=listing)
    if form.is_valid():
      listing = form.save(commit=False)
      listing.seller = request.user
      
      ListingAttribute.objects.filter(listing=listing).delete()
      for key, value in request.POST.items():
        
        if key.startswith('attr_') and not key.startswith('attr_custom_') and value:
          try:
            ListingAttribute.objects.create(listing=listing, value_id=int(value))
          except ValueError:
            continue
            
        elif key.startswith('attr_custom_') and value:
          try:
            attr_id = int(key.split('_')[-1])
            clean_value = value.strip()
            
            try:
              num_val = float(clean_value.replace(',', '.'))
            except ValueError:
              num_val = None
              
            new_filter_val, created = FilterValue.objects.get_or_create(
              attribute_id=attr_id,
              value=clean_value,
              defaults={'numeric_value': num_val}
            )
            
            ListingAttribute.objects.create(listing=listing, value=new_filter_val)
            
          except ValueError:
            continue
      
      if "save_listing" in request.POST:
        listing.status = Listing.Status.VISIBLE
        listing.save()
        return redirect('listing_detail', id=listing.id)
      
      listing.save()
      messages.success(request, "Draft saved successfully.")
      
      if request.headers.get('HX-Request'):
        return render(request, 'partials/messages.html')
      
      return redirect('index')
    elif request.headers.get('HX-Request'):
        messages.error(request, "You must enter name before saving form.")
        return render(request, 'partials/messages.html')


  else:
    form = ListingForm(instance=listing)
  
  return render(request, 'listings/listing_form.html', {'form': form, 'listing': listing})

@login_required
def edit_listing(request, id):
  listing = get_object_or_404(Listing, id=id)
  
  if listing.seller != request.user:
      raise PermissionDenied
    
  if request.method == "POST":
    form = ListingForm(request.POST, request.FILES, instance=listing)
    if form.is_valid():
      
      ListingAttribute.objects.filter(listing=listing).delete()
      for key, value in request.POST.items():
        
        if key.startswith('attr_') and not key.startswith('attr_custom_') and value:
          try:
            ListingAttribute.objects.create(listing=listing, value_id=int(value))
          except ValueError:
            continue
            
        elif key.startswith('attr_custom_') and value:
          try:
            attr_id = int(key.split('_')[-1])
            clean_value = value.strip()
            
            try:
              num_val = float(clean_value.replace(',', '.'))
            except ValueError:
              num_val = None
              
            new_filter_val, created = FilterValue.objects.get_or_create(
              attribute_id=attr_id,
              value=clean_value,
              defaults={'numeric_value': num_val}
            )
            
            ListingAttribute.objects.create(listing=listing, value=new_filter_val)
            
          except ValueError:
            continue
      
      
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
  
  if "draft" in request.POST:
    messages.info(request, "Draft cleared successfully.")
    
    if request.headers.get('HX-Request'):
      response = HttpResponse()
      response['HX-Redirect'] = reverse('create_listing')
      return response
      
    return redirect('create_listing')
  
  messages.info(request, "Listing deleted successfully.")
  return redirect('index')

@login_required
@require_POST
def delete_listing_image(request, id):
  try:
    image = get_object_or_404(ListingImage, id=id, listing__seller=request.user)
    listing = image.listing
    was_main = image.is_main

    image.delete()

    if was_main:
      next_image = listing.images.order_by('position').first()
      if next_image:
        next_image.is_main = True
        next_image.save()
        
  except ListingImage.DoesNotExist:
    return HttpResponse(status=404)
  
  # Re-render the partial snippet so the layout grid instantly updates via HTMX
  return render(request, 'listings/partials/listing_images_snippet.html', {'listing': listing})

@login_required
@require_POST
def upload_listing_images(request, listing_id):
  listing = get_object_or_404(Listing, id=listing_id, seller=request.user)
  files = request.FILES.getlist('images')
  
  if not files and not listing.images.exists():
    return HttpResponse(
      '<p class="text-xs font-semibold text-red-400">At least one image file is required.</p>',
      status=422,
      headers={"HX-Retarget": "#image-error-message"}
    )
  
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

@login_required
@require_POST
def set_main_image(request, id):
  target_image = get_object_or_404(ListingImage, id=id, listing__seller=request.user)
  listing = target_image.listing
  
  other_images = listing.images.exclude(id=id).order_by('position')
  
  target_image.is_main = True
  target_image.position = 1
  target_image.save()
  
  for index, img in enumerate(other_images, start=2):
    img.is_main = False
    img.position = index
    img.save()
    
  return render(request, 'listings/partials/listing_images_snippet.html', {'listing': listing})
@login_required
@require_POST
def move_image(request, id, direction):
  current_image = get_object_or_404(ListingImage, id=id, listing__seller=request.user)
  listing = current_image.listing
  
  # Fetch ONLY secondary images sorted cleanly by position index
  gallery = list(listing.images.filter(is_main=False).order_by('position'))
  
  try:
    idx = gallery.index(current_image)
  except ValueError:
    # Fallback safety check if called on a main image
    return render(request, 'listings/partials/listing_images_snippet.html', {'listing': listing})
  
  if direction == 'left' and idx > 0:
    other_image = gallery[idx - 1]
    current_image.position, other_image.position = other_image.position, current_image.position
    current_image.save()
    other_image.save()
    
  elif direction == 'right' and idx < len(gallery) - 1:
    other_image = gallery[idx + 1]
    current_image.position, other_image.position = other_image.position, current_image.position
    current_image.save()
    other_image.save()

  return render(request, 'listings/partials/listing_images_snippet.html', {'listing': listing})

def get_attributes_for_category(request):
  category_id = request.GET.get('equipment_type')
  listing_id = request.GET.get('listing_id')
  
  if not category_id:
    return HttpResponse("")
    
  category = get_object_or_404(EquipmentType, id=category_id)
  attributes = category.filter_options.all()
  
  existing_values = {}
  existing_text_values = {}
  
  if listing_id and listing_id.isdigit():
    # Use select_related to speed up the database query
    existing_attrs = ListingAttribute.objects.filter(listing_id=listing_id).select_related('value', 'value__attribute')
    
    for attr in existing_attrs:
      existing_values[attr.value.attribute_id] = attr.value_id
      
      # NEW: Check if numeric, and pass the browser-safe number format
      if attr.value.attribute.is_numeric and attr.value.numeric_value is not None:
        num = attr.value.numeric_value
        # If it's a whole number (15.0), strip the decimal for a cleaner UI (15)
        existing_text_values[attr.value.attribute_id] = int(num) if num.is_integer() else num
      else:
        existing_text_values[attr.value.attribute_id] = attr.value.value
      
  context = {
    'attributes': attributes,
    'existing_values': existing_values,
    'existing_text_values': existing_text_values
  }
  
  return render(request, 'listings/partials/attributes_form_fields.html', context)