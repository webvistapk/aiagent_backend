from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from licensingapp.models import Company, Employee
from rest_framework import status
from project.commons.common_constants import Role

class RegisterCompanyForExistingUserTests(APITestCase):
    def setUp(self):
        self.url = reverse('register-company-for-existing-user')
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.client.force_authenticate(user=self.user)

        self.valid_payload = {
            "name": "User's New Company",
            "address": "456 Main St, Anytown"
        }

    def test_success_company_registration_for_existing_user(self):
        print("register_company_for_existing_user test_success_company_registration_for_existing_user Executing test: success company registration for existing user")
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertTrue(Company.objects.filter(name="User's New Company").exists())
        self.assertTrue(Employee.objects.filter(user=self.user, company__name="User's New Company", role=Role.ADMIN.value).exists())

    def test_user_already_has_company(self):
        print("register_company_for_existing_user test_user_already_has_company Executing test: user already has company")
        existing_company = Company.objects.create(name='Existing User Company', address='1 Some Place')
        Employee.objects.create(user=self.user, company=existing_company, role=Role.ADMIN.value)

        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn("User is already associated with a company.", response.data['message'])

    def test_invalid_company_data(self):
        print("register_company_for_existing_user test_invalid_company_data Executing test: invalid company data")
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop('name')

        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('name', response.data['errors'])

    def test_unauthenticated_access(self):
        print("register_company_for_existing_user test_unauthenticated_access Executing test: unauthenticated access")
        self.client.logout()
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")
