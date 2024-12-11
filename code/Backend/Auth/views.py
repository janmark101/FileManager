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
from Backend.settings import KEYCLOAK_ADMIN, KEYCLOAK_OPENID
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection, KeycloakOpenID
from FoldersFiles.utils import get_scope_id
import uuid
import requests
from .models import UserProfile
from datetime import datetime, timedelta
import jwt
from cryptography.hazmat.primitives import serialization



public_key_path = 'public_key.pem'

with open(public_key_path, 'rb') as f:
    public_key = f.read()

public_key = serialization.load_pem_public_key(public_key)

private_key_path = 'private_key.pem'

with open(private_key_path, 'rb') as f:
    private_key = f.read()

private_key = serialization.load_pem_private_key(private_key, password=None)





keycloak_connection = KeycloakOpenIDConnection(server_url=KEYCLOAK_ADMIN['URL'],
                                               username=KEYCLOAK_ADMIN['USERNAME'],
                                               password=KEYCLOAK_ADMIN['PASSWORD'],
                                               realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                                               client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                                               client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                               verify=True)


keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_OPENID['URL'],
                                 client_id=KEYCLOAK_OPENID['CLIENT_ID'],
                                 realm_name=KEYCLOAK_OPENID['REALM_NAME']
                                 )


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
        team = TeamSerialzer(data=request.data)
        if team.is_valid():
            team = team.save()
            return Response({'response' : 'Team created!'}, status=status.HTTP_201_CREATED)
        return Response(team.errors,status = status.HTTP_400_BAD_REQUEST)
    
    
class TeamObjectView(APIView):
    
    def get(self,request,id):
        team = get_object_or_404(Team,id=id)
        serializer = TeamSerialzer(team,many=False)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request,id):
        team = get_object_or_404(Team,id=id)
        
        if team.team_owner.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])

        team_resources = list(filter(lambda resource : int(resource['attributes']['team'][0]) == team.id, resources))

        try:
            for resource in team_resources:
                keycloak_admin.delete_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                            resource_id=resource['_id'])
            team.delete()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self,request,id):
        team = get_object_or_404(Team, id=id)
        
        if team.team_owner.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = TeamSerialzer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
class JoinTeamView(APIView):
    
    def get(self,request,code):
        team = get_object_or_404(Team,adding_link_code=code)
        
        if team.code_is_valid():
            if request.user in team.users.all():
                return Response({"Error":f"Already in {team.name}!"},status=status.HTTP_409_CONFLICT)
            team.users.add(request.user)

            resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            
            team_resources = list(filter(lambda resource : int(resource['attributes']['team'][0]) == team.id, resources))
            try:
                for resource in team_resources:
                    keycloak_admin.create_client_authz_scope_permission(
                        client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                        payload={
                            "type": "resource",
                            "logic": "POSITIVE",
                            "description" : f"{resource['_id']}_{get_scope_id('No Access')}_{team.id}",
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
        
        if team.team_owner.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
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
        
        if request.user.id != team.team_owner.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if user.id == team.team_owner.id:
            return Response({"error" : "Can't delete team owner!"},status=status.HTTP_403_FORBIDDEN)
        
        
        try:
            permissions = keycloak_admin.get_client_authz_permissions(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            deleted_user_permissions = list(filter(lambda permission : int(permission['name'].split('_')[0]) == user_id and 
                                                int(permission['description'].split('_')[2]) == team.id, permissions))
            
            for permission in deleted_user_permissions:
                url = f"{KEYCLOAK_ADMIN['URL']}/admin/realms/Realm-dev/clients/{KEYCLOAK_ADMIN['CLIENT_ID_KEY']}/authz/resource-server/policy/{permission['id']}"
                access_token = keycloak_connection.token['access_token']
                headers = {
                    'Authorization': f'Bearer {access_token}'
                }
                
                response = requests.delete(url, headers=headers)
            team.users.remove(user)
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class UserObjectView(APIView):
    def patch(self,request):
        user = get_object_or_404(User, id=request.user.id)
        user_profile = get_object_or_404(UserProfile, user=user)
        
        payload = request.data.get('payload')
        
        if request.data.get('hash'): ## do zmiany
            hash = request.data.get('hash')
            
            try:
                resp = keycloak_admin.set_user_password(user_id=user_profile.keycloak_id,
                                                        password=payload['password'],
                                                        temporary=False)
                
                return Response(status=status.HTTP_200_OK)
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        else:
            
            if 'email' in payload:
                try:
                    data = jwt.decode(payload['email'], public_key, algorithms=['RS256'])
                
                except jwt.ExpiredSignatureError:
                    return Response(status=status.HTTP_410_GONE)
                except jwt.InvalidTokenError:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                
                payload = {
                    "email" : data['new_email']
                }

                try:
                    keycloak_admin.update_user(user_id=user_profile.keycloak_id,
                                               payload=payload)
                    return Response(status=status.HTTP_200_OK)
                except Exception as e:
                    print(str(e))
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                
            
            try:
                keycloak_admin.update_user(user_id=user_profile.keycloak_id,
                                        payload=payload)
                
                if 'firstName' in payload:
                    user.first_name = payload['firstName']
                if 'lastName' in payload:
                    user.last_name = payload['lastName']
                if 'email' in payload:
                    user.email = payload['email']
                
                user.save()
            except Exception as e:
                print(str(e))
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(status=status.HTTP_200_OK)
        
    
    def delete(self,request):
        pass


class UserEmailChangeToken(APIView):
    def post(self,request):        
        user = get_object_or_404(User, id=request.user.id)
        user_profile = get_object_or_404(UserProfile, user=user)
        
        new_email = request.data.get('email')
        
        payload = {
            "user" : user_profile.keycloak_id,
            "new_email" : new_email,
            "exp" : datetime.utcnow() + timedelta(minutes=10)
        }
        
        token = jwt.encode(payload,private_key,algorithm='RS256')
        return Response(token, status=status.HTTP_200_OK)
