from unittest.mock import patch
from django.test import RequestFactory
from rest_framework_simplejwt.tokens import AccessToken
from .KeycloakAuth import KeycloakAuthentication
from django.test import TestCase
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin
from Backend.settings import KEYCLOAK_ADMIN, KEYCLOAK_OPENID
from .models import UserProfile
from django.contrib.auth.models import User

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_OPENID['URL'],
                                 client_id=KEYCLOAK_OPENID['CLIENT_ID'],
                                 realm_name=KEYCLOAK_OPENID['REALM_NAME'],
                                 client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                 )




"""
Middleware Tests
"""

def create_user(token : str):
    user_info = keycloak_openid.userinfo(token)
    userprofile, created = UserProfile.objects.get_or_create(keycloak_id=user_info.get('sub'))
    user = User.objects.create(username='tester')
    userprofile.user=user
    userprofile.save()
    return user


class MiddlewareTestCase(TestCase):
    def test_authenticate_valid_token(self):
        created_token = keycloak_openid.token(username='tester',grant_type=["password"], password='123')['access_token']
        created_user = create_user(created_token)
        factory = RequestFactory()
        request = factory.get("/")
        request.headers = {"Authorization": f"Bearer {created_token}"}
        auth = KeycloakAuthentication()


        with patch.object(auth, "get_validated_token") as mock_validate, \
            patch.object(auth, "get_user") as mock_get_user:
            mock_token = AccessToken()
            mock_validate.return_value = mock_token
            mock_get_user.return_value = "test_user"


            user, token = auth.authenticate(request)

            assert user == created_user
            assert token == created_token


    def test_authenticate_invalid_token(self):

        factory = RequestFactory()
        request = factory.get("/")
        request.headers = {"Authorization": "Bearer invalid_token"}
        auth = KeycloakAuthentication()


        with patch.object(auth, "get_validated_token", side_effect=Exception):
            response = auth.authenticate(request)

            assert response is None



    def test_authenticate_no_token(self):
        factory = RequestFactory()
        request = factory.get("/")
        auth = KeycloakAuthentication()

        response = auth.authenticate(request)

        assert response is None
        # assert token is None