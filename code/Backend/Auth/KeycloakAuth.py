from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import  TokenError
from keycloak import KeycloakOpenID, KeycloakAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfile
from Backend.settings import KEYCLOAK_ADMIN, KEYCLOAK_OPENID
from django.contrib.auth.models import User



keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_OPENID['URL'],
                                 client_id=KEYCLOAK_OPENID['CLIENT_ID'],
                                 realm_name=KEYCLOAK_OPENID['REALM_NAME']
                                 )


keycloak_admin = KeycloakAdmin(server_url=KEYCLOAK_ADMIN['URL'],
                                username=KEYCLOAK_ADMIN['USERNAME'],
                                password=KEYCLOAK_ADMIN['PASSWORD'],
                                realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                                client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                                client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                verify=False
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
            # UntypedToken(token)
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