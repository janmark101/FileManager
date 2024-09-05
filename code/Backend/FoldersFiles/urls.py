
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('addfile/',views.UploadFileView.as_view()),
    path('teams/<int:id>/', views.FoldersForTeamView.as_view()),
    path('teams/<int:tid>/<int:fid>', views.SubFoldersView.as_view()),
    path('download/<path:file_path>/', views.download_file, name='download_file'),
    path('file/<int:id>/',views.FileObjectView.as_view())
]
