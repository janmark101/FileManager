
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('teams/',views.TeamView.as_view()),
    path('teams/<int:id>/',views.TeamObjectView.as_view()),
    path('teams/<int:id>/addinglink/',views.AddingLinkView.as_view()),
    path('teams/join/<str:code>',views.JoinTeamView.as_view())
]
