from django.db import models
import os
from django.utils.text import slugify
from django.db.models.signals import post_delete
from django.dispatch import receiver

def get_upload_path(instance, filename : str):
    ext = filename.split('.')[-1]
    
    if hasattr(instance, 'listing'):
      name = f"img_{instance.position}"
      return os.path.join('listings', slugify(instance.listing.name), f"{name}.{ext}")
  
    elif hasattr(instance, 'user'):
      return os.path.join('profiles', slugify(instance.user.username), f"profile_picture.{ext}")
    
    return os.path.join('others', filename)

class Image(models.Model):
  file = models.ImageField(upload_to=get_upload_path)
  uploaded_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    abstract = True # template only
    
    
class ListingImage(Image):
  position = models.PositiveIntegerField(default=1)
  is_main = models.BooleanField()
  listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='images')
  
  def __str__(self):
     return f"{slugify(self.listing.name)}-{self.position}"
  
class ProfilePicture(Image):
  user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='profile_picture')  
  
  def __str__(self):
     return f"{slugify(self.user.username)}"


@receiver(post_delete, sender=ListingImage)
@receiver(post_delete, sender=ProfilePicture)
def delete_empty_folders(sender, instance, **kwargs):
  if not instance.file:
    return

  try:
    folder_path = os.path.dirname(instance.file.path)
    if os.path.exists(folder_path):
      files_in_folder = os.listdir(folder_path)
      current_file = os.path.basename(instance.file.path)
      
      if not files_in_folder or (len(files_in_folder) == 1 and files_in_folder[0] == current_file):
        if os.path.exists(instance.file.path):
          os.remove(instance.file.path)
        
        os.rmdir(folder_path)
  except Exception as e:
    pass