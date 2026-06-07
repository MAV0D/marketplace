from django import forms
from django.utils.safestring import mark_safe
from .models import Listing, EquipmentType

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
    
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    if 'condition' in self.fields:
      choices = list(self.fields['condition'].choices)
      if choices and choices[0][0] == '':
          choices[0] = ('', 'Select a condition...')
      self.fields['condition'].choices = choices
    
    if 'equipment_type' in self.fields:
      self.fields['equipment_type'].choices = self._get_category_choices()
      
  def _get_category_choices(self):
    categories = EquipmentType.objects.all()
    
    children_map = {}
    for cat in categories:
      children_map.setdefault(cat.parent_id, []).append(cat)
      
    choices = [('', 'Select a category...')]
    
    def add_choices(parent_id, depth):
      children = sorted(children_map.get(parent_id, []), key=lambda x: x.name)
      for child in children:
        spaces = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
        choices.append((child.id, mark_safe(f"{spaces}{child.name}")))
        
        add_choices(child.id, depth + 1)
        
    add_choices(None, 0)
    
    return choices
    
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
