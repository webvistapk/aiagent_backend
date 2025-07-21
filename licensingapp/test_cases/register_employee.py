from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType, Company, Employee, CompanyLicense
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta
from django.utils import timezone
from project.commons.common_constants import Role

class RegisterEmployeeTests(APITestCase):
    def setUp(self):
        self.url = reverse('register-employee-by-admin')
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_company = Company.objects.create(name='Admin Company', address='123 Admin St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.license_type = LicenseType.objects.create(
            name='Pro License',
            duration=1,
            duration_type='years',
            price_per_user='100.00'
        )

        self.active_license = CompanyLicense.objects.create(
            company=self.admin_company,
            license_type=self.license_type,
            total_users=2, # Admin + 1 more user allowed initially
            total_amount='200.00',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            status='active'
        )

        self.valid_payload = {
            "username": "newemployee",
            "password": "employeepassword",
            "email": "employee@example.com",
            "first_name": "Emp",
            "last_name": "One"
        }

    def test_success(self):
        print("Test successful employee registration by admin")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertTrue(User.objects.filter(username='newemployee').exists())
        self.assertTrue(Employee.objects.filter(user__username='newemployee', company=self.admin_company, role=Role.USER.value).exists())
        self.assertEqual(Employee.objects.filter(company=self.admin_company).count(), 2) # Admin + new employee

    def test_duplicate_username(self):
        print("Test employee registration with duplicate username")
        User.objects.create_user(username='existinguser', password='password123')
        payload = self.valid_payload.copy()
        payload['username'] = 'existinguser'

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('username', response.data['errors'])

    def test_no_capacity(self):
        print("Test employee registration when no license capacity is available")
        # Reduce total_users to 1 (only admin is allowed)
        self.active_license.total_users = 1
        self.active_license.save()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "No more capacity available for new employees on the current license.")

    def test_invalid_data(self):
        print("Test employee registration with invalid data")
        payload = self.valid_payload.copy()
        payload.pop('username') # Missing username

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('username', response.data['errors'])

    def test_unauthenticated(self):
        print("Test employee registration without authentication")
        self.client.credentials() # Clear credentials
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin(self):
        print("Test employee registration by a non-admin user")
        non_admin_user = User.objects.create_user(username='regularuser', password='userpassword')
        Employee.objects.create(user=non_admin_user, company=self.admin_company, role=Role.USER.value)
        non_admin_access_token = str(AccessToken.for_user(non_admin_user))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + non_admin_access_token)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_admin_employee_not_found(self):
        print("Test employee registration when admin employee is not found for the user")
        user_without_employee = User.objects.create_user(username='noemployee', password='pass')
        token_no_employee = str(AccessToken.for_user(user_without_employee))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_no_employee)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
