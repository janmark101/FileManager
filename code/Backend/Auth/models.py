from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    keycloak_id = models.CharField(max_length=255,unique=True,null=False,blank=False)
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return str(self.user)

class Team(models.Model):
    name = models.CharField(max_length=255, null=False,blank=False)
    users = models.ManyToManyField(User,blank=True,related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    team_owner = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)
    adding_link_code = models.CharField(max_length=16,null=True,blank=True,unique=True)
    adding_link_code_expiration_time = models.DateTimeField(blank=True,null=True)
    description = models.TextField(max_length=500, null=True, blank=True, default="")

    def __str__(self):
        return self.name
    
    def code_is_valid(self):
        expiration_time = self.adding_link_code_expiration_time
        return expiration_time is not None and expiration_time > timezone.now()
    
    class Meta:
        ordering =['id']


