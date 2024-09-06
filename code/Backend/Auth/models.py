from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=255, null=False,blank=False)
    users = models.ManyToManyField(User,blank=True,related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    team_owner = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering =['id']
# Create your models here.
