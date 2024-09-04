from django.db import models
from django.contrib.auth.models import User
import os
from django.utils.text import slugify
from Auth.models import Team

# Create your models here.
class Folder(models.Model):
    team = models.ForeignKey(Team,null=False,blank=False,on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self',null=True,blank=True, related_name='subfolders', on_delete=models.CASCADE)
    owner = models.ForeignKey(User,null=False,blank=False,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    

def upload_to(instance, filename):
    folder_name = slugify(instance.folder.name)
    return os.path.join(folder_name, filename)


class File(models.Model):
    file = models.FileField(upload_to=upload_to)
    folder = models.ForeignKey(Folder, related_name='files', null=True, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(User,null=False,blank=False,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name