from .models import File
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import File
from .serializers import FileSerializer
from Auth.models import Team
from django.shortcuts import get_object_or_404
from Auth.serializers import TeamSerialzer, UserPermissionSerializer
from django.http import FileResponse, Http404
import os
from Backend.settings import KEYCLOAK_ADMIN
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection, KeycloakUMA
from keycloak.exceptions import KeycloakPostError, KeycloakPutError
from .utils import get_scope_id, get_permissions_for_resource, get_scopes_id, get_sub_resources, get_resource_by_team, \
    get_resource_parent_resources, get_sub_resources_to_delete, get_scope_by_id
import uuid
from django.contrib.auth.models import User


keycloak_connection = KeycloakOpenIDConnection(server_url=KEYCLOAK_ADMIN['URL'],
                                               username=KEYCLOAK_ADMIN['USERNAME'],
                                               password=KEYCLOAK_ADMIN['PASSWORD'],
                                               realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                                               client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                                               client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                               verify=True)


keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

keycloak_uma = KeycloakUMA(connection=keycloak_connection)


def download_file(request, file_path):
    # file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    file_full_path = '/app/' + file_path 
    if os.path.exists(file_full_path):
        response = FileResponse(open(file_full_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_full_path)}"'
        return response
    else:
        raise Http404("File does not exist.")



class UploadFileView(APIView):
    def post(self, request,id):

        resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])

        resource = list(filter(lambda resource : resource['_id'] == id,resources))

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_instance = File.objects.create(file=uploaded_file,
                                            folder=resource[0]['_id'])
        
        serializer = FileSerializer(file_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ResourceForTeamView(APIView):

    def get(self,request,id):
        team = get_object_or_404(Team,id=id)
        resources = keycloak_admin.get_client_authz_resources(
            client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY']
            )
                                
        resources_filtered = list(filter(lambda resource : get_resource_by_team(resource=resource,
                                                                       team_id=team.id),resources))
        
        
        fixed_resources = [{"name" : res['name'].split('/')[1], "id" : res['_id']} for res in resources_filtered]
        
        team_serializer = TeamSerialzer(team,many=False)

        return Response({"team" :team_serializer.data,"folders" : fixed_resources},status=status.HTTP_200_OK)
    
    def post(self,request,id):
        team = get_object_or_404(Team, id=id)
        resource_name = request.data.get('name')
        
        parent_resource_id  = request.data.get('parent_resource')
        
        payload = {
            "name": f"{team.id}/{resource_name}",
            "type": "Folder",
            "attributes": {
                "created_by": request.user.id,
                "team": team.id,
                "parent_resource": request.data.get('parent_resource')
            },
            "uris": [],
            "scopes": ["no_access", "default", "part_access", "full_access"]
        }
        
        if parent_resource_id != 'None':
            parent_resource = keycloak_admin.get_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                                       resource_id=parent_resource_id)
            
            payload['name'] = f"{parent_resource['name']}/{resource_name}"
        
        try:
            resource_data = keycloak_admin.create_client_authz_resource(
                client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                payload=payload
            )
            
            scope = get_scope_id(scope=request.data.get('scope'))
            try : 
                res = keycloak_admin.create_client_authz_scope_permission(
                        client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                        payload={
                            "type": "resource",
                            "logic": "POSITIVE",
                            "description" : f"{resource_data['_id']}_{get_scope_id('Full Access')}",
                            "decisionStrategy": "UNANIMOUS",
                            "name": f"{request.user.id}_{uuid.uuid4()}",
                            "resources": [
                                resource_data['_id']
                                ],
                            "scopes": [
                                get_scope_id('Full Access')]
                            ,
                            "policies": [
                                
                            ]
                        }
                    )
                

                for user in team.users.all():
                    if user.id == request.user.id:
                        continue
                    keycloak_admin.create_client_authz_scope_permission(
                        client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                        payload={
                            "type": "resource",
                            "logic": "POSITIVE",
                            "description" : f"{resource_data['_id']}_{scope}",
                            "decisionStrategy": "UNANIMOUS",
                            "name": f"{user.id}_{uuid.uuid4()}",
                            "resources": [
                                resource_data['_id']
                                ],
                            "scopes": [
                                scope]
                            ,
                            "policies": [
                                
                            ]
                        }
                    )
            except KeycloakPostError as e:
                keycloak_admin.delete_client_authz_resource(
                    client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                    resource_id=resource_data['_id']
                )
                return Response({"error": "Failed to create permission"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(status=status.HTTP_201_CREATED)
        
        except KeycloakPostError as e:
            print(str(e))
            if e.response_code == 409:
                return Response({"error": "Folder with this name already exists!"}, status=status.HTTP_409_CONFLICT)
        
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class SubResourcesView(APIView):
    
    def get(self,request,tid,fid):
        
        team = get_object_or_404(Team,id=tid)
        
        
        
        resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])

        resources_filtered = list(filter(lambda res : get_sub_resources(resource=res,
                                                            team_id=team.id,
                                                            parent_folder_id=fid), resources)) 
                
        
        fixed_resources = [{"name" : resource['name'].rsplit('/',1)[1], "id" : resource['_id']} for resource in resources_filtered]
        
        files = File.objects.filter(folder=fid)
        file_serializer = FileSerializer(files,many=True)

        team_serializer = TeamSerialzer(team,many=False)
        
        resource_names, resource_ids = get_resource_parent_resources(resources=resources,
                                                                      resource_id=fid)
        
        return Response({"folders" : fixed_resources, "files":file_serializer.data,"team" : team_serializer.data,"resource_names" : resource_names[::-1], "resource_ids" : resource_ids[::-1] },status=status.HTTP_200_OK)       
        

class CheckFolderPermissionView(APIView):
    
    def post(self,request,tid,fid):
        
        scopes = request.data.get('scopes')
        
        permissions = keycloak_admin.get_client_authz_permissions(
            client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY']
        )

        find_permission = list(filter(lambda permission : get_permissions_for_resource(permission=permission,
                                                                                       resource_id=fid,
                                                                                       user_id=request.user.id,
                                                                                       scope_key=get_scopes_id(scopes_list=scopes)), permissions))
        
        if find_permission:
            return Response(status=status.HTTP_200_OK)
                
        return Response({'Error':"You dont have permissions to perform this action!"},status=status.HTTP_401_UNAUTHORIZED)   


class FileObjectView(APIView):
    permission_classes=[AllowAny]
    
    def delete(self,request,id):
        file = get_object_or_404(File,id=id)
        file.delete()
        return Response(status=status.HTTP_200_OK)

    def patch(self,request,id):
        file = get_object_or_404(File,id=id)
        
            
        serializer = FileSerializer(file,data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
class FolderObjectView(APIView):    
    def delete(self,request,id):
        try :            
            resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            
            resources_ids = get_sub_resources_to_delete(resources=resources,main_folder_id=id, resources_ids=[])

            if resources_ids:
                for resource_id in resources_ids:
                    keycloak_admin.delete_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                                resource_id=resource_id)
                    
            keycloak_admin.delete_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                        resource_id=id)
            
            return Response(status=status.HTTP_200_OK)
        
        except Exception as e :
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def patch(self,request,id):
        
        resource = keycloak_admin.get_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                            resource_id=id)
        
        payload = {
            "name": "",
            "type": "Folder",
            "attributes": {
                "created_by": request.user.id,
                "team": 13,
                "parent_resource": resource['attributes']['parent_resource']
            },
            "uris": [],
            "scopes": ["no_access", "default", "part_access", "full_access"]
        }
        
        
        parent_resource_id = request.data.get('parent_resource')

        if parent_resource_id:
            parent_resource = keycloak_admin.get_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                                       resource_id=parent_resource_id)
            payload['attributes']['parent_resource'] = parent_resource_id
            payload['name'] = f"{parent_resource['name']}/{resource['name'].rsplit('/',1)[1]}"
            
        else:
            payload['name'] = f"{resource['name'].rsplit('/',1)[0]}/{request.data.get('name')}"
        
        try:
            keycloak_admin.update_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                                resource_id=id,
                                                                payload=payload)
            
            return Response(status=status.HTTP_200_OK)
            
        except KeycloakPutError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

import requests      
class FolderPermissions(APIView):
    def get(self,request,id):
        resource_id = id
        
        try:
            permissions = keycloak_admin.get_client_authz_permissions(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            filtered_permissions = list(filter(lambda per : per['description'].split('_')[0] == resource_id, permissions))
        
            permissions_ = [{"user" :int(permission['name'].split('_')[0]), "permission" : get_scope_by_id(permission['description'].split('_')[1]), "permission_name" : permission['name'], \
                "permission_id" : permission['id']} for permission in filtered_permissions]
                        
            for permission in permissions_ : 
                user = get_object_or_404(User,id=permission['user'])
                user_data = UserPermissionSerializer(user,many=False)
                permission['user'] = user_data.data
                
            return Response({"permissions" : permissions_}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def post(self,request,id):
        print(request.data.get('permissions'))
        
        try:
            for perm in request.data.get('permissions'):
                
                access_token = keycloak_connection.token['access_token']

                url = f"{KEYCLOAK_ADMIN['URL']}/admin/realms/Realm-dev/clients/{KEYCLOAK_ADMIN['CLIENT_ID_KEY']}/authz/resource-server/policy/{perm['permission_id']}"

                headers = {
                    'Authorization': f'Bearer {access_token}'
                }
                
                response = requests.delete(url, headers=headers)
                
                
                payload={
                    "type": "resource",
                    "logic": "POSITIVE",
                    "description" : f"{id}_{get_scope_id(perm['permission'])}",
                    "decisionStrategy": "UNANIMOUS",
                    "name": f"{perm['permission_name']}",
                    "resources": [
                        id
                        ],
                    "scopes": [
                        get_scope_id(perm['permission'])
                        ]
                    ,
                    "policies": [
                        
                        ]
                    }
                       
                res = keycloak_admin.create_client_authz_scope_permission(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                                          payload=payload)
                        
                
                
                
                
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)