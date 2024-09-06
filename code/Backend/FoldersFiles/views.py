from django.shortcuts import render
from .models import File,Folder
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import File, Folder
from .serializers import FileSerializer, FolderSerializer, FolderAddSerializer
from rest_framework.authentication import TokenAuthentication
from Auth.models import Team
from django.shortcuts import get_object_or_404
from Auth.serializers import TeamSerialzer
from django.db.models import Q
from django.http import FileResponse, Http404
import os
from django.conf import settings

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
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def post(self, request,id):
        folder = get_object_or_404(Folder,id=id)
        print(request)
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
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def get(self,request,id):
        team = get_object_or_404(Team,id=id)
        team_serializer = TeamSerialzer(team,many=False)
        folders = Folder.objects.filter(
            Q(team=team) & Q(parent_folder__isnull=True)
        )
        folders_serializer = FolderSerializer(folders,many=True)
        return Response({"team" :team_serializer.data,"folders" :folders_serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request,id):
        team = get_object_or_404(Team,id=id)
        
        folder = FolderAddSerializer(data=request.data)
        if folder.is_valid():
            folder.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(folder.errors,status=status.HTTP_400_BAD_REQUEST)
    
class SubFoldersView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
    def get(self,request,tid,fid):
        team = get_object_or_404(Team,id=tid)
        folder = get_object_or_404(Folder,id=fid)
        
        folder_names = []
        folder_ids = []
        while folder.parent_folder is not None:
            folder_names.append(folder.name)
            folder_ids.append(folder.id)
            folder = folder.parent_folder
        
        folder_ids.append(folder.id)
        folder_names.append(folder.name)
        rev_folder_names = []
        rev_folder_ids = []
        
        for i in range(len(folder_names)-1,-1,-1):
            rev_folder_names.append(folder_names[i])
            rev_folder_ids.append(folder_ids[i])
                
        folders = Folder.objects.filter(parent_folder_id=fid)
        files = File.objects.filter(folder=fid)
        files_serializer = FileSerializer(files,many=True)
        team_serializer = TeamSerialzer(team,many=False)
        folders_serializer = FolderSerializer(folders,many=True)
        return Response({"team" : team_serializer.data,"folders" : folders_serializer.data,"files":files_serializer.data,"folder_names_ids" : [rev_folder_names,rev_folder_ids]}, status=status.HTTP_200_OK)
        
        

class FileObjectView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
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
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
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