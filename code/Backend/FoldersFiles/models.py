from django.db import models
import os
from django.utils.text import slugify
from Auth.models import Team


def upload_to(instance, filename):
    folder_name = slugify(instance.resource)
    return os.path.join(folder_name, filename)


class File(models.Model):
    file = models.FileField(upload_to=upload_to)
    resource = models.CharField(max_length=50,null=False,blank=False)
    name = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_extension = models.CharField(max_length=10, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        
        if self.file:
            _, extension = os.path.splitext(self.file.name)
            self.file_extension = extension.lower()
            
        super().save(*args,**kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering=['id']
        
