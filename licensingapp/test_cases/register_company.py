from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from licensingapp.models import Company, Employee
from rest_framework import status

class RegisterCompanyTests(APITestCase):
    def setUp(self):
        self.url = reverse('register-company')
        self.valid_payload = {
            "user": {
                "username": "newuser",
                "password": "newpassword123",
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User"
            },
            "company": {
                "name": "New Company Ltd",
                "address": "123 New Street, New City"
            }
        }

    def test_success(self):
        print("Test successful company registration")
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Company.objects.filter(name='New Company Ltd').exists())
        self.assertTrue(Employee.objects.filter(user__username='newuser', role='admin').exists())

    def test_duplicate_username(self):
        print("Test registration with duplicate username")
        User.objects.create_user(username='existinguser', password='password123')
        payload = self.valid_payload.copy()
        payload['user']['username'] = 'existinguser'

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('username', response.data['errors']['user'])

    def test_invalid_user_data(self):
        print("Test registration with invalid user data")
        payload = self.valid_payload.copy()
        payload['user'].pop('username') # Missing username

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('username', response.data['errors']['user'])

    def test_invalid_company_data(self):
        print("Test registration with invalid company data")
        payload = self.valid_payload.copy()
        payload['company'].pop('name') # Missing company name

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('name', response.data['errors']['company'])

    def test_missing_user_field(self):
        print("Test registration with missing 'user' top-level field")
        payload = self.valid_payload.copy()
        payload.pop('user')

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('user', response.data['errors'])

    def test_missing_company_field(self):
        print("Test registration with missing 'company' top-level field")
        payload = self.valid_payload.copy()
        payload.pop('company')

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('company', response.data['errors'])