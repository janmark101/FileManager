from .models import File
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import FileSerializer
from Auth.models import Team
from django.shortcuts import get_object_or_404
from Auth.serializers import TeamSerialzer, UserPermissionSerializer
from django.http import FileResponse, Http404
import os
from Backend.settings import KEYCLOAK_ADMIN, MEDIA_ROOT, BASE_DIR
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from keycloak.exceptions import KeycloakPostError, KeycloakPutError
from .utils import get_scope_id, get_permissions_for_resource, get_scopes_id, get_sub_resources, get_resource_by_team, \
    get_resource_parent_resources, get_sub_resources_to_delete, get_scope_by_id
import uuid
from django.contrib.auth.models import User
from typing import List




keycloak_connection = KeycloakOpenIDConnection(server_url=KEYCLOAK_ADMIN['URL'],
                                               username=KEYCLOAK_ADMIN['USERNAME'],
                                               password=KEYCLOAK_ADMIN['PASSWORD'],
                                               realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                                               client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                                               client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                               verify=True)


keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

# keycloak_uma = KeycloakUMA(connection=keycloak_connection)


def download_file(request, file_path):
    """
    Function to download file from server via browser
    
    # Args :
        request
        file_path -> file path to download
        
    # Retrun :
        file or Http404 error
    """
    file_full_path = os.path.join(BASE_DIR, file_path)
    # file_full_path = '/app' + file_path 

    if os.path.exists(file_full_path):
        response = FileResponse(open(file_full_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_full_path)}"'
        return response
    else:
        raise Http404("File does not exist.")


def check_permission(scopes : List[str], fid : str, user_id : int) -> bool:
    """
    Function to check if user have specific permission
    
    # Args :
        scopes : List[str] -> list of permissions to check if user have
        fid : str -> resource id 
        user_id : int -> user id
        
    # Retrun :
        bool -> True if user have permission othervise false
    """
    permissions = keycloak_admin.get_client_authz_permissions(
        client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY']
    )

    find_permission = list(filter(lambda permission : get_permissions_for_resource(permission=permission,
                                                                                    resource_id=fid,
                                                                                    user_id=user_id,
                                                                                    scope_key=get_scopes_id(scopes_list=scopes)), permissions))
    
    if find_permission:
        return True
            
    return False 


class UploadFileView(APIView):
    def post(self, request,id):
        """
        Function to upload file to specific resource
        
        # Args :
            request
            id -> resource id 
            
        # Retrun :
            Http201 if successfully uploaded file othervise Http400
        """

        resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])

        resource = list(filter(lambda resource : resource['_id'] == id,resources))

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_instance = File.objects.create(file=uploaded_file,
                                            resource=resource[0]['_id'])
        
        serializer = FileSerializer(file_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ResourceForTeamView(APIView):
    """
    View to create and get team's resources
    """
    def get(self,request,id):
        """
        Function to get all team's resources where parent_resource is none 
        
        # Args :
            request
            id -> team id 
            
        # Retrun :
            Http200 with list contains all resources
        """
        team = get_object_or_404(Team,id=id)

        if (request.user not in team.users.all() and team.team_owner.id != request.user.id):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        resources = keycloak_admin.get_client_authz_resources(
            client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY']
            )
                                
        resources_filtered = list(filter(lambda resource : get_resource_by_team(resource=resource,
                                                                       team_id=team.id),resources))
        
        
        fixed_resources = [{"name" : res['name'].split('/')[1], "id" : res['_id']} for res in resources_filtered]
        
        team_serializer = TeamSerialzer(team,many=False)

        return Response({"team" :team_serializer.data,"resources" : fixed_resources, "user" : request.user.id},status=status.HTTP_200_OK)
    
    def post(self,request,id):
        """
        Function to create new resource in team and create permissions for newly created resource
        
        # Args :
            request
            id -> team id 
            
        # Retrun :
            Http201 when all was good otherwise Http500 
        """
        print(id, "team id")
        team = get_object_or_404(Team, id=id)
        
        if (request.user not in team.users.all() and team.team_owner.id != request.user.id):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
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
                            "description" : f"{resource_data['_id']}_{get_scope_id('Full Access')}_{team.id}",
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
                
                if team.team_owner.id != request.user.id:
                    keycloak_admin.create_client_authz_scope_permission(
                        client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                        payload={
                            "type": "resource",
                            "logic": "POSITIVE",
                            "description" : f"{resource_data['_id']}_{get_scope_id('Full Access')}_{team.id}",
                            "decisionStrategy": "UNANIMOUS",
                            "name": f"{team.team_owner.id}_{uuid.uuid4()}",
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
                            "description" : f"{resource_data['_id']}_{scope}_{team.id}",
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
        """
        Function to get all resources where parent_resource is equal to fid
        
        # Args :
            request
            fid -> parent resource id 
            tid -> team id
            
        # Retrun :
            Http200 
        """
        
        team = get_object_or_404(Team,id=tid)
        
        if check_permission(['Default','Part Access','Full Access'], fid, request.user.id) == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        
        if (request.user not in team.users.all() and team.team_owner.id != request.user.id):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])

        resources_filtered = list(filter(lambda res : get_sub_resources(resource=res,
                                                            team_id=team.id,
                                                            parent_resource_id=fid), resources)) 
                
        
        fixed_resources = [{"name" : resource['name'].rsplit('/',1)[1], "id" : resource['_id']} for resource in resources_filtered]
        
        files = File.objects.filter(resource=fid)
        file_serializer = FileSerializer(files,many=True)

        team_serializer = TeamSerialzer(team,many=False)
        
        resource_names, resource_ids = get_resource_parent_resources(resources=resources,
                                                                      resource_id=fid)
        
        return Response({"resources" : fixed_resources, "files":file_serializer.data,"team" : team_serializer.data,"resource_names" : resource_names[::-1], "resource_ids" : resource_ids[::-1], "user" : request.user.id },status=status.HTTP_200_OK)       
        


class CheckResourcePermissionView(APIView):
    
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
            return Response({"Success" : "Have permission."},status=status.HTTP_200_OK)
                
        return Response({'Error':"You dont have permissions to perform this action!"},status=status.HTTP_403_FORBIDDEN)   
    

class FileObjectView(APIView):
    """
    View to manage files 
    """
    permission_classes=[AllowAny]
    
    def delete(self,request,id):
        """
        Function to delete specific file 
        
        # Args :
            request
            id -> file id 
            
        # Retrun :
            Http200 or Http500
        """
        
        file = get_object_or_404(File,id=id)
        if file.file and os.path.isfile(file.file.path):
            try:
                os.remove(file.file.path)
            except OSError as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            file.delete()
        return Response(status=status.HTTP_200_OK)

    def patch(self,request,id):
        """
        Function to update files details
        
        # Args :
            request
            id -> file id 
            
        # Retrun :
            Http200 or Http400
        """
        file = get_object_or_404(File,id=id)
        

        serializer = FileSerializer(file,data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
class ResourceObjectView(APIView):  
    """
    View to manage subresources
    """
    def delete(self,request,id, tid):
        """
        Function to delete specific resource (id) and all resources when parent resource is equal to id
        
        # Args :
            request
            id -> resource id 
            tid -> team id
            
        # Retrun :
            Http200 or Http500
        """
        
        if check_permission(['Full Access'], id, request.user.id) == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        team = get_object_or_404(Team, id=tid)
        
        if (request.user not in team.users.all() and team.team_owner.id != request.user.id):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try :            
            resources = keycloak_admin.get_client_authz_resources(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            
            resources_ids = get_sub_resources_to_delete(resources=resources,main_resource_id=id, resources_ids=[])

            if resources_ids:
                for resource_id in resources_ids:
                    keycloak_admin.delete_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                                resource_id=resource_id)
                    
                    files_to_delete = File.objects.filter(resource=resource_id)

                    for file_obj in files_to_delete:
                        if file_obj.file and os.path.isfile(file_obj.file.path):
                            try:
                                os.remove(file_obj.file.path)
                                file_obj.delete()
                            except OSError as e:
                                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            keycloak_admin.delete_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                        resource_id=id)
            
            files_to_delete = File.objects.filter(resource=id)

            for file_obj in files_to_delete:
                if file_obj.file and os.path.isfile(file_obj.file.path):
                    try:
                        os.remove(file_obj.file.path)
                        file_obj.delete()
                    except OSError as e:
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(status=status.HTTP_200_OK)
        
        except Exception as e :
            print(str(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def patch(self,request,id,tid):
        """
        Function to update resource's details
        
        # Args :
            request
            id -> resource id 
            tid -> team id
            
        # Retrun :
            Http200 or Http400
        """
        
        team = get_object_or_404(Team, id=tid)
        
        if (request.user not in team.users.all() and team.team_owner.id != request.user.id):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if check_permission(['Part Access','Full Access'], id, request.user.id) == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        resource = keycloak_admin.get_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                                                            resource_id=id)
        payload = {
            "name": "",
            "type": "Folder",
            "attributes": {
                "created_by": request.user.id,
                "team": resource['attributes']['team'],
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
class ResourcePermissions(APIView):
    """
    View to manage resource's permissions
    """
    def get(self,request,tid,id):
        """
        Function to get all permissions with users for specific resource
        
        # Args :
            request
            id -> resource id 
            tid -> team id
            
        # Retrun :
            Http200 or Http500
        """
        resource_id = id
        
        team = get_object_or_404(Team, id=tid)
        
        if (request.user not in team.users.all() and team.team_owner.id != request.user.id):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if check_permission(['Full Access'], id, request.user.id) == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            permissions = keycloak_admin.get_client_authz_permissions(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
            filtered_permissions = list(filter(lambda per : per['description'].split('_')[0] == resource_id, permissions))
        
            permissions_ = [{"user" :int(permission['name'].split('_')[0]), "permission" : get_scope_by_id(permission['description'].split('_')[1]), "permission_name" : permission['name'], \
                "permission_id" : permission['id']} for permission in filtered_permissions]
                        
            for permission in permissions_ : 
                user = get_object_or_404(User,id=permission['user'])
                user_data = UserPermissionSerializer(user,many=False)
                permission['user'] = user_data.data
                
            return Response(permissions_, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def post(self,request,tid,id):     
        """
        Function to update permissions for specific resource
        
        # Args :
            request
            id -> resource id 
            tid -> team id
            
        # Retrun :
            Http200 or Http500
        """  
        team = get_object_or_404(Team,id=tid)
        
        if (request.user not in team.users.all() and team.team_owner.id != request.user.id):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if check_permission(['Full Access'], id, request.user.id) == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
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
                    "description" : f"{id}_{get_scope_id(perm['permission'])}_{team.id}",
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)