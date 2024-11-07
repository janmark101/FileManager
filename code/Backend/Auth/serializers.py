from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team
        
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
                 
        
        