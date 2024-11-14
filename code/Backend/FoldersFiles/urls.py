from django.urls import path
from . import views

urlpatterns = [
    path('addfile/',views.UploadFileView.as_view()),
    path('teams/<int:id>/', views.ResourceForTeamView.as_view()),
    path('teams/<int:tid>/<str:fid>/', views.SubResourcesView.as_view()),
    path('download/<path:file_path>/', views.download_file, name='download_file'),
    path('file/<int:id>/',views.FileObjectView.as_view()),
    path('folder/<str:id>/',views.FolderObjectView.as_view()),
    path('folder/<str:id>/addfile/',views.UploadFileView.as_view()),
    path('folder/<int:tid>/<str:fid>/permission',views.CheckFolderPermissionView.as_view()),
    path('resource/<str:id>/permissions',views.FolderPermissions.as_view())
]
