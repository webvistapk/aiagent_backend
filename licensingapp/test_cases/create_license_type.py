from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class CreateLicenseTypeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.access_token = str(AccessToken.for_user(self.user))
        self.url = reverse('create-license-type')
        self.payload = {
            "duration": 2,
            "duration_type": "months",
            "price_per_user": "5.00",
            "name": "basic"
        }

    def test_month_success(self):
        print("Test successful creation of a license type with duration in months")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LicenseType.objects.count(), 1)
        self.assertEqual(LicenseType.objects.get().name, 'basic')

    def test_days_success(self):
        print("Test successful creation of a license type with duration in days")
        self.payload['duration_type'] = 'days'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_years_success(self):
        print("Test successful creation of a license type with duration in years")
        self.payload['duration_type'] = 'years'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_incorrect_duration_type(self):
        print("Test failed creation of a license type with duration type incorrect")
        self.payload['duration_type'] = 'yearss'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.payload['duration_type'] = None
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.payload['duration_type'] = 3
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_incorrect_price(self):
        print("Test failed creation of a license type with price incorrect")
        self.payload['price_per_user'] = '5/0'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.payload['price_per_user'] = None
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_incorrect_name(self):
        print("Test failed creation of a license type with price incorrect")
        self.payload['name'] = None
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_incorrect_duration(self):
        print("Test failed creation of a license type with duration incorrect")
        self.payload['duration'] = 'qwdwqdwq'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.payload['duration'] = None
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)