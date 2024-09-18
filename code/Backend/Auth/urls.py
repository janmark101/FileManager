
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
    path('teams/',views.TeamView.as_view()),
    path('teams/<int:id>/',views.TeamObjectView.as_view()),
    path('register/',views.Register.as_view()),

]
