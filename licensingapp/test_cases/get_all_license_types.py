from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class GetAllLicenseTypesTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', password='testpassword')
        self.access_token = str(AccessToken.for_user(self.user))
        self.url = reverse('get-all-license-types')

    def test_success(self):
        print("Test successful retrieval of all license types")
        # Create some license types
        LicenseType.objects.create(name='Basic', duration=1, duration_type='years', price_per_user='10.00')
        LicenseType.objects.create(name='Pro', duration=6, duration_type='months', price_per_user='50.00')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('license_types', response.data)
        self.assertEqual(len(response.data['license_types']), 2)
        self.assertEqual(response.data['license_types'][0]['name'], 'Basic')
        self.assertEqual(response.data['license_types'][1]['name'], 'Pro')

    def test_no_licenses(self):
        print("Test retrieval when no license types exist")
        # No license types are created in setUp, so the database is empty here
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('license_types', response.data)
        self.assertEqual(len(response.data['license_types']), 0)

    def test_unauthenticated(self):
        print("Test retrieval without authentication")
        self.client.credentials() # Clear credentials

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)