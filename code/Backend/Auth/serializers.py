from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team

class UserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(allow_blank=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name' , 'email', 'token']
        
        
class UserTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email']
   
class TeamSerialzer(serializers.ModelSerializer):
    users = UserTeamSerializer(many=True,read_only=True)
    class Meta:
        model=Team
        fields='__all__'
        