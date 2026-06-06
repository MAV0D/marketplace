from django import forms
from .models import Listing
from django.core.exceptions import ValidationError

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
    
    if self.data and 'save_draft' in self.data:
      return cleaned_data
    
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
      raise forms.ValidationError("You must upload at least one image before your listing can be published.")

    equipment_type = cleaned_data.get('equipment_type')
    
    if equipment_type:
      required_attrs = equipment_type.filter_options.all()
      
      for attr in required_attrs:
        val_dropdown = self.data.get(f'attr_{attr.id}')
        val_custom = self.data.get(f'attr_custom_{attr.id}')
        
        if not val_dropdown and not val_custom:
          self.add_error(None, f"The specification '{attr.name}' is required to publish this listing.")
      
    return cleaned_data
  
  def full_clean(self, *args, **kwargs):
    super().full_clean(*args, **kwargs)
    
    if self.data and 'save_draft' in self.data:
      for field_name in list(self._errors.keys()):
        if 'required' in [err.code for err in self._errors[field_name].as_data()] and field_name != "name":
          del self._errors[field_name]
