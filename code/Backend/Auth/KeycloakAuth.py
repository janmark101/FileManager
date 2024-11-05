from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID, KeycloakAdmin
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


keycloak_admin = KeycloakAdmin(server_url="http://localhost:8080",
                                username='admin',
                                password='admin',
                                realm_name="Realm-dev",
                                client_id='django-app',
                                client_secret_key='V60bjjUkroQUklc7TO9yCN3wZ5xr4cUp',
                                verify=False)


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
            # UntypedToken(token)
            user_info = keycloak_openid.userinfo(token)
            print(token)
            # print(keycloak_admin.get_client_authz_resources(client_id='94558e4b-6a12-4bde-88f7-a9d36dcd14a9'))
            # print(keycloak_admin.get_client_authz_permissions(client_id='94558e4b-6a12-4bde-88f7-a9d36dcd14a9'))
            keycloak_admin.create_client_authz_resource_based_permission(client_id='94558e4b-6a12-4bde-88f7-a9d36dcd14a9',
                payload={
        "type": "resource",
        "logic": "POSITIVE",
        "decisionStrategy": "UNANIMOUS",
        "name": "Oby zadzialalo prosze",
        "resources": [
            '089b7b64-96d6-4ff5-b47f-e0fa22b1f1be'
        ],
        "policies": [
            
        ]
                }
            )
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