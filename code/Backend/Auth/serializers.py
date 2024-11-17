from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team
        
class UserTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email']
   
class TeamSerialzer(serializers.ModelSerializer):
    users = UserTeamSerializer(many=True,read_only=True)
    team_owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    class Meta:
        model=Team
        fields='__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Jeśli to GET, zserializuj pełny obiekt użytkownika
        representation['team_owner'] = UserTeamSerializer(instance.team_owner).data
        return representation
       
class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','first_name', 'last_name']
        
        