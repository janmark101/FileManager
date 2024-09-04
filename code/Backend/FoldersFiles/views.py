from django.shortcuts import render
from .models import File,Folder
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import File, Folder
from .serializers import FileSerializer, FolderSerializer
from rest_framework.authentication import TokenAuthentication
from Auth.models import Team
from django.shortcuts import get_object_or_404
from Auth.serializers import TeamSerialzer
from django.db.models import Q

class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def post(self, request, *args, **kwargs):
        folder_id = request.data.get('folder_id')
        folder = Folder.objects.get(id=folder_id)

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_instance = File.objects.create(
            name=uploaded_file.name,
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
    
class SubFoldersView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
    def get(self,request,tid,fid):
        team = get_object_or_404(Team,id=tid)
        folder = get_object_or_404(Folder,id=fid)
        
        folder_names = []
        while folder.parent_folder is not None:
            folder_names.append(folder.name)
            folder = folder.parent_folder
        
        folder_names.append(folder.name)
        rev_folder_names = []
        
        for name in reversed(folder_names):
            rev_folder_names.append(name)
                
        folders = Folder.objects.filter(parent_folder_id=fid)
        files = File.objects.filter(folder=fid)
        files_serializer = FileSerializer(files,many=True)
        team_serializer = TeamSerialzer(team,many=False)
        folders_serializer = FolderSerializer(folders,many=True)
        return Response({"team" : team_serializer.data,"folders" : folders_serializer.data,"files":files_serializer.data,"folder_names" : rev_folder_names}, status=status.HTTP_200_OK)
        
        

from django.http import FileResponse, Http404
import os
from django.conf import settings

def download_file(request, file_path):
    file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    file_full_path = '/app/' + file_path 
    print(settings.MEDIA_ROOT,"media root")
    print(file_full_path, " E KURWA")
    if os.path.exists(file_full_path):
        response = FileResponse(open(file_full_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_full_path)}"'
        return response
    else:
        raise Http404("File does not exist.")
