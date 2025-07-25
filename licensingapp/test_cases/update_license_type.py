from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class UpdateLicenseTypeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', password='testpassword')
        self.access_token = str(AccessToken.for_user(self.user))

        self.license_type = LicenseType.objects.create(
            name='Standard License',
            duration=1,
            duration_type='years',
            price_per_user='10.00'
        )
        self.update_url = reverse('update-license-type', args=[self.license_type.id])

    def test_success(self):
        print("update_license_type test_success Test successful update of a license type")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        payload = {
            "name": "Premium License",
            "duration": 3,
            "duration_type": "months",
            "price_per_user": "25.50"
        }

        response = self.client.patch(self.update_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "License type updated successfully")
        self.assertEqual(response.data['status'], "success")

        updated_license_type = LicenseType.objects.get(id=self.license_type.id)
        self.assertEqual(updated_license_type.name, payload['name'])
        self.assertEqual(updated_license_type.duration, payload['duration'])
        self.assertEqual(updated_license_type.duration_type, payload['duration_type'])
        self.assertEqual(str(updated_license_type.price_per_user), payload['price_per_user'])

    def test_not_found(self):
        print("update_license_type test_not_found Test update of a non-existent license type")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        non_existent_id = self.license_type.id + 999
        url = reverse('update-license-type', args=[non_existent_id])
        payload = {"name": "Non Existent License"}

        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "License type not found")

    def test_invalid_data(self):
        print("update_license_type test_invalid_data Test update with invalid data")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        payload = {
            "name": "Invalid License",
            "duration": "not_a_number",
            "duration_type": "days",
            "price_per_user": "10.00"
        }

        response = self.client.patch(self.update_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('duration', response.data['errors'])

    def test_unauthenticated(self):
        print("update_license_type test_unauthenticated Test update without authentication")
        self.client.credentials()
        payload = {"name": "Unauthorized Update"}

        response = self.client.patch(self.update_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
