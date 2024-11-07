from django.shortcuts import render
from .models import File,Folder
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import File, Folder, FolderRole
from .serializers import FileSerializer, FolderSerializer, FolderAddSerializer
from rest_framework.authentication import TokenAuthentication
from Auth.models import Team, TeamRoles
from django.shortcuts import get_object_or_404
from Auth.serializers import TeamSerialzer
from django.db.models import Q
from django.http import FileResponse, Http404
import os
from Backend.settings import KEYCLOAK_ADMIN
import requests
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from keycloak.exceptions import KeycloakPostError
from .utils import get_scope_id, get_permissions_for_resource, get_scopes_id
import uuid

keycloak_connection = KeycloakOpenIDConnection(
                server_url=KEYCLOAK_ADMIN['URL'],
                username=KEYCLOAK_ADMIN['USERNAME'],
                password=KEYCLOAK_ADMIN['PASSWORD'],
                realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                verify=True
                )

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)


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
    permission_classes=[AllowAny]

    def post(self, request,id):
        folder = get_object_or_404(Folder,id=id)
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_instance = File.objects.create(
            file=uploaded_file,
            folder=folder,
            owner=request.user
        )
        serializer = FileSerializer(file_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FoldersForTeamView(APIView):

    def get(self,request,id):
        team = get_object_or_404(Team,id=id)
        resources = keycloak_admin.get_client_authz_resources(
            client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY']
            )
                        
        def get_resource_by_team(resource) -> bool:
            attributes = resource['attributes']
            return attributes['team'][0] == str(team.id)
        
        resources = list(filter(get_resource_by_team,resources))
        
        fixed_resources = [{"name" : res['name'], "id" : res['_id']} for res in resources]
        
        team_serializer = TeamSerialzer(team,many=False)

        return Response({"team" :team_serializer.data,"folders" : fixed_resources},status=status.HTTP_200_OK)
    
    def post(self,request,id):
        team = get_object_or_404(Team, id=id)
        folder_name = request.data.get('name')
        
        payload = {
            "name": f"{team.id}/{folder_name}",
            "type": "Folder",
            "attributes": {
                "created_by": request.user.id,
                "team": team.id,
                "subfolder": 'None'
            },
            "uris": [f"{team.id}/{folder_name}"],
            "scopes": ["no_access", "default", "part_access", "full_access"]
        }
        
        try:
            resource_data = keycloak_admin.create_client_authz_resource(
                client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                payload=payload
            )
            
            scope = get_scope_id(scope=request.data.get('scope'))
            try : 
                keycloak_admin.create_client_authz_scope_permission(
                        client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                        payload={
                            "type": "resource",
                            "logic": "POSITIVE",
                            "description" : f"{resource_data['_id']}_{get_scope_id('full_access')}",
                            "decisionStrategy": "UNANIMOUS",
                            "name": f"{request.user.id}_{uuid.uuid4()}",
                            "resources": [
                                resource_data['_id']
                                ],
                            "scopes": [
                                get_scope_id('full_access')]
                            ,
                            "policies": [
                                
                            ]
                        }
                    )
                
                for user in team.users.all():
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
                print(f"Error creating scope permission for user {user.id}: {e}")
                keycloak_admin.delete_client_authz_resource(
                    client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
                    resource_id=resource_data['_id']
                )
                return Response({"error": "Failed to create permission"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(status=status.HTTP_201_CREATED)
        
        except KeycloakPostError as e:
            print(f"Error creating resource: {e}")
            if e.response_code == 409:
                return Response({"error": "Folder with this name already exists!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # team = get_object_or_404(Team,id=id)
        # token = get_access_token()
        # url = 'http://localhost:8080/realms/Realm-dev/authz/protection/resource_set'
        # print(request.user)
        # data = {
        #     "name" : f"{team.id}/{request.data.get('name')}",
        #     "type" : "Folder",
        #     "attributes": {
        #     "folder_id": "unique-folder-id",
        #     "created_by" : request.user.id
        #     },
        #     "uris": [f"{team.id}/{request.data.get('name')}"],
        #     "scopes": ["no_access", "default", "part_access", "full_access"]
        # }
        
        # headers = {
        #     "Authorization": f"Bearer {token}",
        #     "Content-Type": "application/json"
        # }
        
        # response = requests.post(url=url, json=data,headers=headers)
        
        # if response.status_code == 409:
        #     return Response(status=status.HTTP_409_CONFLICT)
        # if response.status_code == 200:
        #     folder_id = response.json()['_id']
        #     for user in team.users.all():
        #         pass
        #     print(response.json())
        #     return Response(status=status.HTTP_201_CREATED)
        # print(response.json())
        # return Response(status=status.HTTP_201_CREATED)
        # team = get_object_or_404(Team,id=id)
        
        # if Folder.objects.filter(team=team,name=request.data.get('name')).exists() and request.data.get('parent_folder') is None:
        #     return Response({"Error" : "Folder with this name already exists!"},status=status.HTTP_400_BAD_REQUEST)
        
        # if Folder.objects.filter(team=team,name=request.data.get('name'),parent_folder=request.data.get('parent_folder')).exists() and request.data.get('parent_folder') is not None:
        #     return Response({"Error" : "Folder with this name already exists!"},status=status.HTTP_400_BAD_REQUEST)
        
        # if request.data.get('parent_folder') is None:
        #     user_role_in_team = get_object_or_404(TeamRoles,team=team, user=request.user)
        #     if user_role_in_team.is_default:
        #         return Response({"error":"You dont have permissions to perform this action!"},status=status.HTTP_401_UNAUTHORIZED)
        
        # folder = FolderAddSerializer(data=request.data)
        # if folder.is_valid():
        #     folder = folder.save()
        #     FolderRole.objects.create(user=request.user,folder=folder,role='full_access')
        #     for user in team.users.all():
        #         FolderRole.objects.create(user=user,folder=folder,role='no_access')
        #     return Response(status=status.HTTP_201_CREATED)
        # return Response(folder.errors,status=status.HTTP_400_BAD_REQUEST)
    
class SubFoldersView(APIView):
    permission_classes=[AllowAny]
    
    def get(self,request,tid,fid):
        
        team = get_object_or_404(Team,id=tid)
        # folder = get_object_or_404(Folder,id=fid)
        

                
        print("JESTEM TU ")
        # user_folder_role = get_object_or_404(FolderRole,folder=folder,user=request.user)
        # if user_folder_role.has_no_access:
        #     return Response({'Error':"You dont have permissions to perform this action!"},status=status.HTTP_401_UNAUTHORIZED)
        
        # folder_names = []
        # folder_ids = []
        # while folder.parent_folder is not None:
        #     folder_names.append(folder.name)
        #     folder_ids.append(folder.id)
        #     folder = folder.parent_folder
        
        # folder_ids.append(folder.id)
        # folder_names.append(folder.name)
        # rev_folder_names = []
        # rev_folder_ids = []
        
        # for i in range(len(folder_names)-1,-1,-1):
        #     rev_folder_names.append(folder_names[i])
        #     rev_folder_ids.append(folder_ids[i])
                
        # folders = Folder.objects.filter(parent_folder_id=fid)
        # files = File.objects.filter(folder=fid)
        # files_serializer = FileSerializer(files,many=True)
        # team_serializer = TeamSerialzer(team,many=False)
        # folders_serializer = FolderSerializer(folders,many=True)
        return Response( status=status.HTTP_200_OK)
        

class CheckFolderPermissionView(APIView):
    
    def post(self,request,tid,fid):
        
        scopes = request.data.get('scopes')
        
        permissions = keycloak_admin.get_client_authz_permissions(
            client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY']
        )
        print(scopes)
        find_permission = list(filter(lambda permission : get_permissions_for_resource(
                                                                                permission=permission,
                                                                                resource_id=fid,
                                                                                user_id=request.user.id,
                                                                                scope_key=get_scopes_id(scopes_list=scopes)
                                                                                  ), permissions))
        
        print(find_permission)
        if find_permission:
            return Response(status=status.HTTP_200_OK)
                
        return Response({'Error':"You dont have permissions to perform this action!"},status=status.HTTP_401_UNAUTHORIZED)   
        
        
        # keycloak_admin.get_client_authz_scope_permission(
        #     client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'],
        #     scope_id='490ad6d1-69ab-43c3-931e-6827efdfbfd5'
        # )
        
        # user_folder_role = get_object_or_404(FolderRole,folder=folder,user=request.user)
        # if user_folder_role.has_no_access:
        #     return Response({'Error':"You dont have permissions to perform this action!"},status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(status=status.HTTP_200_OK)
        

class FileObjectView(APIView):
    permission_classes=[AllowAny]
    
    def delete(self,request,id):
        file = get_object_or_404(File,id=id)
        file.delete()
        return Response(status=status.HTTP_200_OK)

    def patch(self,request,id):
        file = get_object_or_404(File,id=id)
        
        print(request.data)
        if request.data.get('folder'):
            get_object_or_404(Folder,id=request.data.get('folder'))
            
        serializer = FileSerializer(file,data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
class FolderObjectView(APIView):
    permission_classes=[AllowAny]
    
    def delete(self,request,id):
        folder = get_object_or_404(Folder,id=id)
        folder.delete()
        return Response(status=status.HTTP_200_OK)

    def patch(self,request,id):
        folder = get_object_or_404(Folder,id=id)

        if request.data.get('parent_folder'):
            temp = get_object_or_404(Folder,id=request.data.get('parent_folder'))
            folder.parent_folder = temp
            folder.save()
            return Response(status=status.HTTP_200_OK)
        
        serializer = FolderSerializer(folder,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)