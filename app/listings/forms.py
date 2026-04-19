from django import forms
from .models import Listing
from django.core.exceptions import ValidationError


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'accept': 'image/*'})) # Přidáno omezení pro prohlížeč
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            # Validace velikosti (např. max 5MB na soubor)
            MAX_UPLOAD_SIZE = 5 * 1024 * 1024
            
            result = []
            for d in data:
                if d.size > MAX_UPLOAD_SIZE:
                    raise ValidationError(f"Soubor {d.name} je příliš velký. Maximum je 5MB.")
                
                # Tato část zajistí, že každý soubor je skutečně obrázek
                # (Django interně zkusí otevřít soubor pomocí Pillow)
                res = single_file_clean(d, initial)
                result.append(res)
        else:
            result = single_file_clean(data, initial)
        return result

class NewListingForm(forms.ModelForm):
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