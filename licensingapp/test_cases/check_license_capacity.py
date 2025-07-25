from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType, Company, Employee, CompanyLicense
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta
from django.utils import timezone
from project.commons.common_constants import Role

class CheckLicenseCapacityTests(APITestCase):
    def setUp(self):
        self.url = reverse('check-license-capacity')
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_company = Company.objects.create(name='Admin Company', address='123 Admin St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.license_type = LicenseType.objects.create(
            name='Capacity License',
            duration=1,
            duration_type='years',
            price_per_user='10.00'
        )

        self.active_license = CompanyLicense.objects.create(
            company=self.admin_company,
            license_type=self.license_type,
            total_users=5,
            total_amount='50.00',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            status='active'
        )

        self.existing_user = User.objects.create_user(username='existinguser', password='password123')
        self.existing_employee = Employee.objects.create(user=self.existing_user, company=self.admin_company, role=Role.USER.value)

    def test_success(self):
        print("check_license_capacity test_success Test successful retrieval of license capacity")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['current_employees'], 2)
        self.assertEqual(response.data['data']['allowed_users'], 5)
        self.assertEqual(response.data['data']['users_left'], 3)

    def test_no_active_license(self):
        print("check_license_capacity test_no_active_license Test retrieval when no active license exists")
        self.active_license.status = 'inactive'
        self.active_license.save()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "No active license found for this company")

    def test_unauthenticated(self):
        print("check_license_capacity test_unauthenticated Test license capacity check without authentication")
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin(self):
        print("check_license_capacity test_not_admin Test license capacity check by a non-admin user")
        non_admin_user = User.objects.create_user(username='regularuser', password='userpassword')
        Employee.objects.create(user=non_admin_user, company=self.admin_company, role=Role.USER.value)
        non_admin_access_token = str(AccessToken.for_user(non_admin_user))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + non_admin_access_token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_employee_not_found_for_user(self):
        print("check_license_capacity test_employee_not_found_for_user Test license capacity check when employee is not found for the user")
        user_without_employee = User.objects.create_user(username='noemployee', password='pass')
        token_no_employee = str(AccessToken.for_user(user_without_employee))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_no_employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
