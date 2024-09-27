from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team
from django.contrib.auth.password_validation import validate_password

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
    # team_owner = serializers.HiddenField(default=serializers.CurrentUserDefault())   
    class Meta:
        model=Team
        fields='__all__'
        # read_only_fields = ['team_owner']
                 
        
class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,allow_blank=False)
    first_name = serializers.CharField(required=False,allow_blank=True)
    last_name = serializers.CharField(required=False,allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate_password(self,value):
        validate_password(value)
        return value
    
    def validate_username(self,value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already in use!')
        return value
    
    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already in use!')
        return value
    
    def create(self,validated_data):
        user=User.objects.create(**validated_data)
        return user        
        
   
        