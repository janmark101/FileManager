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
from django.contrib.auth.models import User
from Backend.settings import KEYCLOAK_ADMIN
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from FoldersFiles.utils import get_scope_id
import uuid
import requests


keycloak_connection = KeycloakOpenIDConnection(server_url=KEYCLOAK_ADMIN['URL'],
                                               username=KEYCLOAK_ADMIN['USERNAME'],
                                               password=KEYCLOAK_ADMIN['PASSWORD'],
                                               realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                                               client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                                               client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                               verify=True)


keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

class TeamView(APIView):
    def get(self,request):
        teams_owner = Team.objects.filter(team_owner=request.user.id)
        teams_part = Team.objects.filter(users__id=request.user.id)
        teams = list(chain(teams_owner, teams_part))
        serializer = TeamSerialzer(teams,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        request.data['team_owner'] = request.user.id
        print(request.data)
        team = TeamSerialzer(data=request.data)
        if team.is_valid():
            team = team.save()
            # TeamRoles.objects.create(
            #     team=team,
            #     user=request.user,
            #     role='admin'
            # )
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
        
        resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            
        team_resources = list(filter(lambda resource : int(resource['attributes']['team'][0]) == team.id, resources))
        
        try:
            for resource in team_resources:
                keycloak_admin.delete_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                            resource_id=resource['_id'])
            
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class JoinTeamView(APIView):
    
    def get(self,request,code):
        team = get_object_or_404(Team,adding_link_code=code)
        
        if team.code_is_valid():
            if request.user in team.users.all():
                return Response({"Error":f"Already in {team.name}!"},status=status.HTTP_409_CONFLICT)
            team.users.add(request.user)
            # TeamRoles.objects.create(user=request.user,team=team,role='default')
            resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            
            team_resources = list(filter(lambda resource : int(resource['attributes']['team'][0]) == team.id, resources))
            try:
                for resource in team_resources:
                    keycloak_admin.create_client_authz_scope_permission(
                        client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                        payload={
                            "type": "resource",
                            "logic": "POSITIVE",
                            "description" : f"{resource['_id']}_{get_scope_id('No Access')}",
                            "decisionStrategy": "UNANIMOUS",
                            "name": f"{request.user.id}_{uuid.uuid4()}",
                            "resources": [
                                resource['_id']
                                ],
                            "scopes": [
                                get_scope_id('No Access')]
                            ,
                            "policies": [
                                
                            ]
                        }
                    )
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            
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
    
    
class DeleteUserFromTeam(APIView):
    def delete(self,request,id, user_id):
        team = get_object_or_404(Team, id=id)
        
        user = get_object_or_404(User, id = user_id)
        
        if user.id == team.team_owner.id:
            return Response({"error" : "Can't delete team owner!"},status=status.HTTP_403_FORBIDDEN)
        
        team.users.remove(user)
        
        permissions = keycloak_admin.get_client_authz_permissions(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
        deleted_user_permissions = list(filter(lambda permission : int(permission['name'].split('_')[0]) == user_id, permissions))
        
        for permission in deleted_user_permissions:
            url = f"{KEYCLOAK_ADMIN['URL']}/admin/realms/Realm-dev/clients/{KEYCLOAK_ADMIN['CLIENT_ID_KEY']}/authz/resource-server/policy/{permission['id']}"
            access_token = keycloak_connection.token['access_token']
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.delete(url, headers=headers)
        
        return Response(status=status.HTTP_200_OK)
