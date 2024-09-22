from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID
from django.conf import settings
from keycloak.exceptions import KeycloakConnectionError


keycloak_openid = KeycloakOpenID(server_url="http://gifted_goldwasser:8080",
                                 client_id="angular-app",
                                 realm_name="dive-dev"
                                 )


import jwt

import requests




class KeycloakMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            print(decoded_token)
            try:
                # Weryfikacja JWT
                print("barier")
                user_info = keycloak_openid.userinfo(token) # post na ten url z tokenem dziala http://localhost:8080/realms/dive-dev/protocol/openid-connect/userinfo
                #https://chatgpt.com/share/66ed6c91-c0f0-8006-aba2-bf91bd52a7c2 
                request.user = user_info
                print(user_info,"user")
            except (InvalidToken, TokenError) as e:
                print(f"Token error: {str(e)}")
                print("siema")
                request.user = None
                request.user_roles = []

            return None
        else:
            token = None
            return None
