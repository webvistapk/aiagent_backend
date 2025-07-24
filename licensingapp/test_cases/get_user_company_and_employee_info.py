from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from licensingapp.models import Company, Employee, LicenseType
from rest_framework import status
from project.commons.common_constants import Role, DurationType

class GetUserCompanyAndEmployeeInfoTests(APITestCase):
    def setUp(self):
        self.url = reverse('get-user-company-employee-info')
        self.password = 'testpassword'

        self.user_no_company = User.objects.create_user(username='nocmpuser', password=self.password, email='nocmp@example.com')

        self.user_with_company = User.objects.create_user(username='cmpuser', password=self.password, email='cmp@example.com', first_name='John', last_name='Doe')
        self.company = Company.objects.create(name='Test Company', address='123 Test St')
        self.employee = Employee.objects.create(user=self.user_with_company, company=self.company, role=Role.ADMIN.value)

    def test_success_user_with_company_and_employee(self):
        self.client.force_authenticate(user=self.user_with_company)
        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIsNotNone(response.data['data']['company'])
        self.assertIsNotNone(response.data['data']['employee'])

        self.assertEqual(response.data['data']['company']['name'], self.company.name)
        self.assertEqual(response.data['data']['company']['address'], self.company.address)

        self.assertEqual(response.data['data']['employee']['user']['username'], self.user_with_company.username)
        self.assertEqual(response.data['data']['employee']['user']['first_name'], self.user_with_company.first_name)
        self.assertEqual(response.data['data']['employee']['user']['last_name'], self.user_with_company.last_name)
        self.assertEqual(response.data['data']['employee']['role'], self.employee.role)

    def test_success_user_without_company_and_employee(self):
        self.client.force_authenticate(user=self.user_no_company)
        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIsNone(response.data['data']['company'])
        self.assertIsNone(response.data['data']['employee'])
        self.assertEqual(response.data['message'], "User company and employee info retrieved successfully")

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")