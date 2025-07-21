from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class GetLicenseTypeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', password='testpassword')
        self.access_token = str(AccessToken.for_user(self.user))

        self.license_type = LicenseType.objects.create(
            name='Standard License',
            duration=1,
            duration_type='years',
            price_per_user='10.00'
        )
        self.get_url = reverse('get-license-type', args=[self.license_type.id])

    def test_success(self):
        print("Test successful retrieval of a license type")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(self.get_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('license', response.data)
        self.assertEqual(len(response.data['license']), 1)
        self.assertEqual(response.data['license'][0]['id'], self.license_type.id)
        self.assertEqual(response.data['license'][0]['name'], self.license_type.name)

    def test_not_found(self):
        print("Test retrieval of a non-existent license type")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        non_existent_id = self.license_type.id + 999
        url = reverse('get-license-type', args=[non_existent_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "License type not found")

    def test_unauthenticated(self):
        print("Test retrieval without authentication")
        self.client.credentials()

        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)