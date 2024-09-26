from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfile
import jwt
from jwt import InvalidTokenError
from django.conf import settings
from django.contrib.auth.models import User


keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080",
                                 client_id="django-app",
                                 realm_name="Realm-dev"
                                 )


import jwt



class KeycloakAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication to create or get logged users from decoding by Keycloak JWT Token
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        
        try:
            UntypedToken(token)
            
            user_info = keycloak_openid.userinfo(token)
            user = self.get_or_create_user(user_info)

            return (user,token)

        except TokenError:
            return None
        
        
    def get_or_create_user(self, user_info):
        """
        Fucntion to get or create user
        """
        user_id = user_info.get('sub') 

        
        userprofile, created = UserProfile.objects.get_or_create(keycloak_id=user_id)

        if created:
            user = User.objects.create(
                email=user_info.get('email'),
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                username=user_info.get('preferred_username', userprofile.keycloak_id),
            )
            userprofile.user = user
            userprofile.save()
        return userprofile.user