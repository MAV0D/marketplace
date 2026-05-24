from django import forms
from .models import Listing
from django.core.exceptions import ValidationError


class MultipleFileInput(forms.ClearableFileInput):
  allow_multiple_selected = True

class MultipleFileField(forms.FileField):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault("widget", MultipleFileInput(attrs={'accept': 'image/*'}))
    super().__init__(*args, **kwargs)

  def clean(self, data, initial=None):
    single_file_clean = super().clean
    if isinstance(data, (list, tuple)):
      MAX_UPLOAD_SIZE = 5 * 1024 * 1024
        
      result = []
      for d in data:
        if d.size > MAX_UPLOAD_SIZE:
          raise ValidationError(f"File {d.name} is too big. Maximum filesize is 5MB.")
        
        res = single_file_clean(d, initial)
        result.append(res)
    else:
      result = single_file_clean(data, initial)
    return result

class ListingForm(forms.ModelForm):
  class Meta:
    model = Listing
    
    fields = ['name',
              'description',
              'for_rent',
              'renting_price',
              'for_sale',
              'selling_price',
              'condition',
              'equipment_type',
            ]
    
  def clean(self):
    cleaned_data = super().clean()
    
    for_rent = cleaned_data.get('for_rent')
    rent_price = cleaned_data.get('renting_price')
    
    for_sale = cleaned_data.get('for_sale')
    sale_price = cleaned_data.get('selling_price')
    
    if not for_rent and not for_sale:
      self.add_error('for_rent', "You must choose at least one option.")
      
    if for_rent and not rent_price:
      self.add_error('renting_price', "You must enter renting price.")
      
    if for_sale and not sale_price:
      self.add_error('selling_price', "You must enter selling price.")
      
    has_db_images = self.instance.pk and self.instance.images.exists()
    has_uploaded_images = bool(self.files.getlist('images'))

    if not has_db_images and not has_uploaded_images:
      raise forms.ValidationError("You must upload at least one image before your listing can be saved or published.")
      
    return cleaned_data