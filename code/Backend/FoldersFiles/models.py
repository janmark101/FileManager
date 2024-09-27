from django.db import models
from django.contrib.auth.models import User
import os
from django.utils.text import slugify
from Auth.models import Team

# Create your models here.
class Folder(models.Model):
    team = models.ForeignKey(Team,null=False,blank=False,on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self',null=True,blank=True, related_name='subfolders', on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering=['id']
    

def upload_to(instance, filename):
    folder_name = slugify(instance.folder.name)
    return os.path.join(folder_name, filename)


class File(models.Model):
    file = models.FileField(upload_to=upload_to)
    folder = models.ForeignKey(Folder, related_name='files', null=False, blank=False, on_delete=models.CASCADE)
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
        
class FolderRole(models.Model):
    ROLE_CHOICES = [
        ('default','default'),
        ('full_access','Full Access'),
        ('part_access', 'Part Access'),
        ('no_access', 'No Access')
    ]
    
    folder = models.ForeignKey(Folder,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=25,choices=ROLE_CHOICES,default=ROLE_CHOICES[3])
    
    class Meta:
        unique_together = ('folder','user')
        
    def __str__(self):
        return f"{self.folder}, {self.user}, {self.role} "
    
    @property
    def has_default(self):
        return self.role=='default'
    
    @property
    def has_full_access(self):
        return self.role=='full_access'
    
    @property
    def has_part_access(self):
        return self.role=='part_access'
    
    @property
    def has_no_access(self):
        return self.role=='no_access'
    
    