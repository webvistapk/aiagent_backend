from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType, Company, Employee, CompanyLicense
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta
from django.utils import timezone
from project.commons.common_constants import Role

class IncreaseTotalUsersTests(APITestCase):
    def setUp(self):
        self.url = reverse('increase-license-users')
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_company = Company.objects.create(name='Admin Company', address='123 Admin St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.license_type = LicenseType.objects.create(
            name='Standard',
            duration=1,
            duration_type='years',
            price_per_user='10.00'
        )

        self.initial_license = CompanyLicense.objects.create(
            company=self.admin_company,
            license_type=self.license_type,
            total_users=5,
            total_amount='50.00',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            status='active'
        )

    def test_success(self):
        print("Test successful increase of total users")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        payload = {"total_users_to_add": 3}

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['message'], "Total users increased successfully")

        self.initial_license.refresh_from_db()
        self.assertEqual(self.initial_license.total_users, 8)
        self.assertEqual(str(self.initial_license.total_amount), '80.00')

    def test_no_active_license(self):
        print("Test increase total users when no active license exists")
        self.initial_license.status = 'inactive'
        self.initial_license.save()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        payload = {"total_users_to_add": 2}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "No active license found for this company")

    def test_invalid_input(self):
        print("Test increase total users with invalid input")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        payload = {"total_users_to_add": 0} # Must be min_value=1
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('total_users_to_add', response.data['errors'])

        payload = {"total_users_to_add": "not_a_number"}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertIn('total_users_to_add', response.data['errors'])

    def test_unauthenticated(self):
        print("Test increase total users without authentication")
        self.client.credentials() # Clear credentials
        payload = {"total_users_to_add": 1}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin(self):
        print("Test increase total users by a non-admin user")
        non_admin_user = User.objects.create_user(username='regularuser', password='userpassword')
        Employee.objects.create(user=non_admin_user, company=self.admin_company, role=Role.USER.value)
        non_admin_access_token = str(AccessToken.for_user(non_admin_user))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + non_admin_access_token)
        payload = {"total_users_to_add": 1}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_employee_not_found_for_user(self):
        print("Test increase total users when employee is not found for the user")
        user_without_employee = User.objects.create_user(username='noemployee', password='pass')
        token_no_employee = str(AccessToken.for_user(user_without_employee))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_no_employee)
        payload = {"total_users_to_add": 1}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)