from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import TeamSerialzer
from .models import Team, TeamRoles
from itertools import chain
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.utils import timezone

class TeamView(APIView):
    def get(self,request):
        teams_owner = Team.objects.filter(team_owner=request.user.id)
        teams_part = Team.objects.filter(users__id=request.user.id)
        teams = list(chain(teams_owner, teams_part))
        serializer = TeamSerialzer(teams,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        request.data['team_owner'] = request.user.id
        team = TeamSerialzer(data=request.data)
        if team.is_valid():
            team = team.save()
            TeamRoles.objects.create(
                team=team,
                user=request.user,
                role='admin'
            )
            return Response({'response' : 'Team created!'}, status=status.HTTP_201_CREATED)
        return Response(team.errors,status = status.HTTP_400_BAD_REQUEST)
    
    
class TeamObjectView(APIView):
    
    def get(self,request,id):
        team = get_object_or_404(Team,id=id)
        serializer = TeamSerialzer(team,many=False)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request,id):
        team = get_object_or_404(Team,id=id)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class JoinTeamView(APIView):
    
    def get(self,request,code):
        team = get_object_or_404(Team,adding_link_code=code)
        
        if team.code_is_valid():
            if request.user in team.users.all():
                return Response({"Error":f"Already in {team.name}!"},status=status.HTTP_409_CONFLICT)
            team.users.add(request.user)
            TeamRoles.objects.create(user=request.user,team=team,role='default')
            return Response({"response" : f"Joined {team.name}"},status=status.HTTP_200_OK)
        
        return Response({"Error" : "The code has expired"},status=status.HTTP_400_BAD_REQUEST)
    
    
class AddingLinkView(APIView):
    
    def get(self,request,id):
        team = get_object_or_404(Team,id=id)
        
        adding_link_code = get_random_string(16)
        while Team.objects.filter(adding_link_code=adding_link_code).exists():
            adding_link_code = get_random_string(16)
            
        team.adding_link_code = adding_link_code
        team.adding_link_code_expiration_time = timezone.now() + timedelta(minutes=10)
        team.save()
        return Response({'link' : adding_link_code},status=status.HTTP_200_OK) 
    
