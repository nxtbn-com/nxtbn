
from django.test import  TestCase
from rest_framework.test import APIClient

from nxtbn.users.tests import UserFactory


from django.contrib.auth.hashers import make_password

class BaseTestCase(TestCase):
    client = APIClient()
    
    def setUp(self):
        self.user = UserFactory(
            email="johndoe@example.com",
            password=make_password('testpass')
        )       
        
    def permissionDenied(self, request, *args, **kwargs):
        self.assertEqual(request.status_code, 403, *args, **kwargs)

    def requestUnauthorized(self, request, *args, **kwargs):
        self.assertEqual(request.status_code, 401, *args, **kwargs)
        
    def assertSuccess(self, request, *args, **kwargs):
        self.assertEqual(request.status_code, 200, *args, **kwargs)
        
    def loginSeccess(self, login):
        self.assertTrue(login)