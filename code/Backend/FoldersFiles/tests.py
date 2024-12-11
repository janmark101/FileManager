from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from .models import File
# from .serializers import FileSerializer, TeamSerializer
from .utils import get_scopes_id, get_permissions_for_resource, get_sub_resources, get_resource_by_team, get_resource_parent_resources
from rest_framework.test import APITestCase
from rest_framework import status
from Auth.models import Team, UserProfile
from cryptography.hazmat.primitives import serialization
from django.contrib.auth.models import User
import unittest
from unittest.mock import patch, MagicMock



"""
Unit tests for the utils.py module
"""

class UnitTests(TestCase):
    def test_get_scopes_id(self):
        scopes = ["Default", "No Access"]
        
        scopes_id = get_scopes_id(scopes)
        
        self.assertEqual(len(scopes_id),2)
        
    def test_get_permissions_for_resource(self):
        user_id = 1
        resource_id ='123'
        
        resource = [
            {"name" : "Test", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "123"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "345"}
        ]
        
        permissions_list = [
            {"id" : "123", 'name' : "1_123", "description" : "123_123_x"},
            {"id" : "345", 'name' : "2_123", "description" : "123_123_x"},
            {"id" : "678", 'name' : "2_123", "description" : "345_123_x"},
            {"id" : "901", 'name' : "1_123", "description" : "345_123_x"},
        ]
        
        
        permissions = list(filter(lambda permission : get_permissions_for_resource(permission=permission,
                                                                                       resource_id=resource_id,
                                                                                       user_id=user_id,
                                                                                       scope_key=["123"]), permissions_list))
        
        self.assertEqual(len(permissions),1)
        
        
    def test_get_sub_resources(self):
        team_id = 32
        
        resources_list = [
            {"name" : "Test", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "1"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "2"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['1']}, '_id' : "3"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['1']}, '_id' : "4"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['3']}, '_id' : "5"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['2']}, '_id' : "6"},
            {"name" : "Test2", "attributes" : {"team" : ['40'], "parent_resource" : ['1']}, '_id' : "7"},
        ]
        
        
        resources = list(filter(lambda resource : get_sub_resources(resource, team_id, "1"), resources_list))
        
        self.assertEqual(len(resources),2)
        
        
    def test_get_resource_by_team(self):
        team_id = 32
        
        resources_list = [
            {"name" : "Test", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "1"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "2"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['1']}, '_id' : "3"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['1']}, '_id' : "4"},
            {"name" : "Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['3']}, '_id' : "5"},
            {"name" : "Test2", "attributes" : {"team" : ['40'], "parent_resource" : ['None']}, '_id' : "6"},
            {"name" : "Test2", "attributes" : {"team" : ['40'], "parent_resource" : ['1']}, '_id' : "7"},
        ]
        
        resources = list(filter(lambda resource : get_resource_by_team(resource, team_id), resources_list))
        
        self.assertEqual(len(resources),2)
        
        
    def test_get_resource_parent_resources(self):
        resource_id = "6"
        
        resources_list = []
        
        names, ids = get_resource_parent_resources(resources_list, resource_id)
            
        self.assertEqual(names, [])
        self.assertEqual(ids, [])
        
        
        resources_list = [
            {"name" : "32/Test", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "1"},
            {"name" : "32/Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "2"},
            {"name" : "32/Test3", "attributes" : {"team" : ['32'], "parent_resource" : ['1']}, '_id' : "3"},
            {"name" : "32/Test4", "attributes" : {"team" : ['32'], "parent_resource" : ['2']}, '_id' : "4"},
            {"name" : "32/Test5", "attributes" : {"team" : ['32'], "parent_resource" : ['3']}, '_id' : "5"},
            {"name" : "32/Test6", "attributes" : {"team" : ['32'], "parent_resource" : ['5']}, '_id' : "6"},
            {"name" : "40/Test7", "attributes" : {"team" : ['40'], "parent_resource" : ['1']}, '_id' : "7"},
        ]
        
        names, ids = get_resource_parent_resources(resources_list, resource_id)
        
        self.assertEqual(len(names), 3)
        self.assertEqual(len(ids), 3)
        
        self.assertEqual(names, ['Test5', 'Test3', 'Test'])
        self.assertEqual(ids, ['5', '3','1'])
        
   
   
class TestKeycloakIntegration(unittest.TestCase):

    @patch('keycloak.KeycloakAdmin.get_client_authz_permissions')
    def test_get_permissions(self, mock_get_permissions):
        # Przygotowanie mocka
        mock_get_permissions.return_value = [
            {"id" : "123", 'name' : "user1_123", "description" : "resource1_123_teamx"},
            {"id" : "345", 'name' : "user2_123", "description" : "resource1_123_teamx"},
            {"id" : "678", 'name' : "user2_123", "description" : "resource2_123_teamx"},
            {"id" : "901", 'name' : "user1_123", "description" : "resource2_123_teamx"},
        ]
        
        keycloak_connection = KeycloakOpenIDConnection(server_url=KEYCLOAK_ADMIN['URL'],
                                                    username=KEYCLOAK_ADMIN['USERNAME'],
                                                    password=KEYCLOAK_ADMIN['PASSWORD'],
                                                    realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                                                    client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                                                    client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                                    verify=True)
        keycloak_admin = KeycloakAdmin(connection=keycloak_connection)


        permissions = keycloak_admin.get_client_authz_permissions(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
        
        
        self.assertEqual(len(permissions), 4)
        self.assertEqual(permissions[0]["id"], "123")
        mock_get_permissions.assert_called_once_with(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
        
        
    @patch('keycloak.KeycloakAdmin.get_client_authz_resource')
    def test_get_resources(self, mock_get_resource):
        mock_get_resource.return_value = [
            {"name" : "32/Test", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "1"},
            {"name" : "32/Test2", "attributes" : {"team" : ['32'], "parent_resource" : ['None']}, '_id' : "2"},
            {"name" : "32/Test3", "attributes" : {"team" : ['32'], "parent_resource" : ['1']}, '_id' : "3"},
            {"name" : "32/Test4", "attributes" : {"team" : ['32'], "parent_resource" : ['2']}, '_id' : "4"},
            {"name" : "32/Test5", "attributes" : {"team" : ['32'], "parent_resource" : ['3']}, '_id' : "5"},
            {"name" : "32/Test6", "attributes" : {"team" : ['32'], "parent_resource" : ['5']}, '_id' : "6"},
            {"name" : "40/Test7", "attributes" : {"team" : ['40'], "parent_resource" : ['1']}, '_id' : "7"},
        ]
        
        keycloak_connection = KeycloakOpenIDConnection(server_url=KEYCLOAK_ADMIN['URL'],
                                                    username=KEYCLOAK_ADMIN['USERNAME'],
                                                    password=KEYCLOAK_ADMIN['PASSWORD'],
                                                    realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
                                                    client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
                                                    client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                                    verify=True)
        keycloak_admin = KeycloakAdmin(connection=keycloak_connection)


        resource = keycloak_admin.get_client_authz_resource(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
        
        

        self.assertEqual(len(resource), 7)
        self.assertEqual(resource[0]["name"], "32/Test")
        mock_get_resource.assert_called_once_with(client_id=KEYCLOAK_ADMIN['CLIENT_ID_KEY'])
   
   
        
"""

"""

from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin
from Backend.settings import KEYCLOAK_ADMIN, KEYCLOAK_OPENID

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_OPENID['URL'],
                                 client_id=KEYCLOAK_OPENID['CLIENT_ID'],
                                 realm_name=KEYCLOAK_OPENID['REALM_NAME'],
                                 client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
                                 )

# keycloak_connection = KeycloakOpenIDConnection(server_url=KEYCLOAK_ADMIN['URL'],
#                                                username=KEYCLOAK_ADMIN['USERNAME'],
#                                                password=KEYCLOAK_ADMIN['PASSWORD'],
#                                                realm_name=KEYCLOAK_ADMIN['REALM_NAME'],
#                                                client_id=KEYCLOAK_ADMIN['CLIENT_ID'],
#                                                client_secret_key=KEYCLOAK_ADMIN['CLIENT_SECRET_KEY'],
#                                                verify=True)
# keycloak_admin = KeycloakAdmin(connection=keycloak_connection)






def create_user(token : str):
    user_info = keycloak_openid.userinfo(token)
    userprofile, created = UserProfile.objects.get_or_create(keycloak_id=user_info.get('sub'))
    user = User.objects.create(username='tester')
    userprofile.user=user
    userprofile.save()
    return user





class ResourceForTeamTest(APITestCase):
    def setUp(self):
        self.token = keycloak_openid.token(username='tester',grant_type=["password"], password='123')['access_token']
        self.user = create_user(self.token)
        self.team = Team.objects.create(name='test',team_owner=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_team_no_exists(self):
        response = self.client.get('/web/teams/100/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_not_in_team(self):
        user = User.objects.create(username='tester2')
        self.team.team_owner = user
        self.team.save()
        response = self.client.get(f'/web/teams/{self.team.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_data(self):
        response = self.client.get(f'/web/teams/{self.team.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user(self):
        self.client.credentials()  
        response = self.client.get('/web/teams/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
class SubResourceTest(APITestCase):
    def setUp(self):
        self.token = keycloak_openid.token(username='tester',grant_type=["password"], password='123')['access_token']
        self.user = create_user(self.token)
        self.team = Team.objects.create(name='test',team_owner=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_team_no_exists(self):
        response = self.client.get('/web/teams/100/123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_dont_have_permission(self):
        response = self.client.get(f'/web/teams/{self.team.id}/123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user(self):
        self.client.credentials()  
        response = self.client.get('/web/teams/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)