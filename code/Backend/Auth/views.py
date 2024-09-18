# views.py
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import  TokenAuthentication
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, TeamSerialzer, RegisterUserSerializer
from django.contrib.auth.models import User
from .models import Team
from django.db.models import Q
from itertools import chain
# from Backend.settings import KEYCLOAK_CLIENT_ID,KEYCLOAK_CLIENT_SECRET,KEYCLOAK_REALM,KEYCLOAK_SERVER_URL

class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username is None or password is None: 
            return Response({'error' : 'You must insert username and password!'},status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        
        if user is not None:
            serializer = UserSerializer(user,many=False).data
            token, created = Token.objects.get_or_create(user=user)
            serializer['token'] = token.key
            return Response({'user':serializer}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
    
class Logout(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
    def post(self,request):
        token = get_object_or_404(Token,user=request.user)
        token.delete()
        return Response({'message':'Logged out succesfully!'},status=status.HTTP_200_OK)
    
    
class Register(APIView):
    permission_classes=[AllowAny]
    
    def post(self,request):
        user = RegisterUserSerializer(data=request.data)
        if user.is_valid():
            user.save()
            return Response(user.data)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamView(APIView):
    permission_classes=[AllowAny]
    
    def get(self,request):
        print(request.user)
        request.user.id=1
        teams_owner = Team.objects.filter(team_owner=request.user.id)
        teams_part = Team.objects.filter(users__id=request.user.id)
        teams = list(chain(teams_owner, teams_part))
        serializer = TeamSerialzer(teams,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        team = TeamSerialzer(data=request.data)
        if team.is_valid():
            team.save()
            return Response({'response' : 'Team created!'}, status=status.HTTP_201_CREATED)
        return Response(team.errors,status = status.HTTP_400_BAD_REQUEST)
    
    
class TeamObjectView(APIView):
    permission_classes=[AllowAny]
    
    def get(self,request,id):
        team = get_object_or_404(Team,id=id)
        serializer = TeamSerialzer(team,many=False)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request,id):
        team = get_object_or_404(Team,id=id)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
