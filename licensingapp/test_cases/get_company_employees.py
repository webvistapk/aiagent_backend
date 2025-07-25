from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import Company, Employee
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from project.commons.common_constants import Role

class GetCompanyEmployeesTests(APITestCase):
    def setUp(self):
        self.url = reverse('get-company-employees')
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_company = Company.objects.create(name='Admin Company', address='123 Admin St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.employee1_user = User.objects.create_user(username='john.doe', password='password1', first_name='John', last_name='Doe')
        self.employee1 = Employee.objects.create(user=self.employee1_user, company=self.admin_company, role=Role.USER.value)

        self.employee2_user = User.objects.create_user(username='jane.smith', password='password2', first_name='Jane', last_name='Smith')
        self.employee2 = Employee.objects.create(user=self.employee2_user, company=self.admin_company, role=Role.USER.value)

        self.other_company = Company.objects.create(name='Other Company', address='456 Other St')
        self.other_employee_user = User.objects.create_user(username='otheruser', password='otherpassword')
        Employee.objects.create(user=self.other_employee_user, company=self.other_company, role=Role.USER.value)

    def test_success(self):
        print("get_company_employees test_success Test successful retrieval of all company employees")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('employees', response.data)
        self.assertEqual(len(response.data['employees']), 3)
        self.assertEqual(response.data['total_count'], 3)
        self.assertFalse(response.data['has_next_page'])

    def test_success_with_pagination(self):
        print("get_company_employees test_success_with_pagination Test successful retrieval with pagination")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        response = self.client.get(f"{self.url}?limit=2&offset=0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['employees']), 2)
        self.assertEqual(response.data['total_count'], 3)
        self.assertTrue(response.data['has_next_page'])
        self.assertEqual(response.data['next_offset'], 2)

        response = self.client.get(f"{self.url}?limit=2&offset=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['employees']), 1)
        self.assertEqual(response.data['total_count'], 3)
        self.assertFalse(response.data['has_next_page'])
        self.assertTrue(response.data['has_previous_page'])
        self.assertEqual(response.data['previous_offset'], 0)

    def test_success_with_filters(self):
        print("get_company_employees test_success_with_filters Test successful retrieval with filters")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        response = self.client.get(f"{self.url}?first_name=John")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['employees']), 1)
        self.assertEqual(response.data['employees'][0]['user']['first_name'], 'John')

        response = self.client.get(f"{self.url}?username=jane")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['employees']), 1)
        self.assertEqual(response.data['employees'][0]['user']['username'], 'jane.smith')

        response = self.client.get(f"{self.url}?last_name=smith")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['employees']), 1)
        self.assertEqual(response.data['employees'][0]['user']['last_name'], 'Smith')

    def test_no_employees(self):
        print("get_company_employees test_no_employees Test retrieval when only admin employee exists")
        self.employee1.delete()
        self.employee2.delete()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('employees', response.data)
        self.assertEqual(len(response.data['employees']), 1)
        self.assertEqual(response.data['employees'][0]['user']['username'], 'admin')
        self.assertEqual(response.data['total_count'], 1)

    def test_unauthenticated(self):
        print("get_company_employees test_unauthenticated Test retrieval without authentication")
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin(self):
        print("get_company_employees test_not_admin Test retrieval by a non-admin user")
        non_admin_user = User.objects.create_user(username='regularuser', password='userpassword')
        Employee.objects.create(user=non_admin_user, company=self.admin_company, role=Role.USER.value)
        non_admin_access_token = str(AccessToken.for_user(non_admin_user))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + non_admin_access_token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_admin_employee_not_found(self):
        print("get_company_employees test_admin_employee_not_found Test retrieval when admin employee is not found for the user")
        user_without_employee = User.objects.create_user(username='noemployee', password='pass')
        token_no_employee = str(AccessToken.for_user(user_without_employee))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_no_employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
