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
  images = MultipleFileField(label="Photos", required=False)
  
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