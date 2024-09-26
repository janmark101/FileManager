from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    keycloak_id = models.CharField(max_length=255,unique=True,null=False,blank=False)
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.user.username

class Team(models.Model):
    name = models.CharField(max_length=255, null=False,blank=False)
    users = models.ManyToManyField(User,blank=True,related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    team_owner = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering =['id']


class TeamRoles(models.Model):
    
    roles = [
        ('manager','Manager'),
        ('default','Default'),
        ('admin','Admin')
    ]
    
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=25,choices=roles,default=roles[1])
    
    def __str__(self):
        return f"{self.team} | {self.role} for {self.user.username}"
