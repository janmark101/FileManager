from django.contrib import admin
from .models import Folder,File, FolderRole

admin.site.register(Folder)
admin.site.register(File)
admin.site.register(FolderRole)
# Register your models here.
