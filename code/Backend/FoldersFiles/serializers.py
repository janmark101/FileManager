# serializers.py
from rest_framework import serializers
from .models import File,Folder
from Auth.serializers import UserSerializer

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ['owner']


class FolderSerializer(serializers.ModelSerializer):
    parent_folder = serializers.SerializerMethodField()
    owner = UserSerializer(many=False,read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'team', 'parent_folder','owner', 'name', 'created_at','updated_at']

    def get_parent_folder(self, obj):
        if obj.parent_folder:
            return FolderSerializer(obj.parent_folder).data
        return None

