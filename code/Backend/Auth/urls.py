
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('teams/',views.TeamView.as_view()),
    path('teams/<int:id>/',views.TeamObjectView.as_view()),
    path('teams/<int:id>/addinglink/',views.AddingLinkView.as_view()),
    path('teams/join/<str:code>/',views.JoinTeamView.as_view()),
    path('teams/<int:id>/<int:user_id>/',views.DeleteUserFromTeam.as_view()),
    path('profile/',views.UserObjectView.as_view()),
    path('token/',views.UserEmailChangeToken.as_view())
]
