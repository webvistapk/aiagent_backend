from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import LicenseType, Company, Employee, CompanyLicense
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta
from django.utils import timezone
from project.commons.common_constants import Role

class ActivateLicenseTests(APITestCase):
    def setUp(self):
        self.url = reverse('activate-license')
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_company = Company.objects.create(name='Admin Company', address='123 Admin St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.license_type_monthly = LicenseType.objects.create(
            name='Monthly Basic',
            duration=1,
            duration_type='months',
            price_per_user='10.00'
        )
        self.license_type_yearly = LicenseType.objects.create(
            name='Yearly Pro',
            duration=1,
            duration_type='years',
            price_per_user='100.00'
        )

    def test_success_new_license(self):
        print("activate_license test_success_new_license Test successful activation of a new license for a company")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        payload = {
            "license_type": self.license_type_monthly.id
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(CompanyLicense.objects.count(), 1)
        new_license = CompanyLicense.objects.first()
        self.assertEqual(new_license.license_type, self.license_type_monthly)
        self.assertEqual(new_license.total_users, 1)
        self.assertEqual(new_license.start_date, timezone.now().date())

    def test_success_extend_license(self):
        print("activate_license test_success_extend_license Test successful activation to extend an existing license")
        initial_license = CompanyLicense.objects.create(
            company=self.admin_company,
            license_type=self.license_type_monthly,
            total_users=5,
            total_amount='50.00',
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=30),
            status='active'
        )

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        payload = {
            "license_type": self.license_type_yearly.id
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(CompanyLicense.objects.count(), 2)
        latest_license = CompanyLicense.objects.order_by('-start_date').first()
        self.assertEqual(latest_license.license_type, self.license_type_yearly)
        self.assertEqual(latest_license.total_users, 5)
        self.assertEqual(latest_license.start_date, initial_license.end_date + timedelta(days=1))

    def test_success_extend_license_without_type_id(self):
        print("activate_license test_success_extend_license_without_type_id Test successful activation to extend an existing license without providing license_type_id")
        initial_license = CompanyLicense.objects.create(
            company=self.admin_company,
            license_type=self.license_type_monthly,
            total_users=5,
            total_amount='50.00',
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=30),
            status='active'
        )

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(CompanyLicense.objects.count(), 2)
        latest_license = CompanyLicense.objects.order_by('-start_date').first()
        self.assertEqual(latest_license.license_type, self.license_type_monthly)
        self.assertEqual(latest_license.total_users, 5)
        self.assertEqual(latest_license.start_date, initial_license.end_date + timedelta(days=1))

    def test_license_type_not_found(self):
        print("activate_license test_license_type_not_found Test activation with non-existent license type ID")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        payload = {
            "license_type": 9999
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "License type not found")

    def test_no_previous_license_and_no_type_id(self):
        print("activate_license test_no_previous_license_and_no_type_id Test activation with no previous license and no license_type ID")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "No previous license found for this company")

    def test_unauthenticated(self):
        print("activate_license test_unauthenticated Test license activation without authentication")
        self.client.credentials()
        payload = {"license_type": self.license_type_monthly.id}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin(self):
        print("activate_license test_not_admin Test license activation by a non-admin user")
        non_admin_user = User.objects.create_user(username='regularuser', password='userpassword')
        Employee.objects.create(user=non_admin_user, company=self.admin_company, role=Role.USER.value)
        non_admin_access_token = str(AccessToken.for_user(non_admin_user))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + non_admin_access_token)
        payload = {"license_type": self.license_type_monthly.id}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_employee_not_found_for_user(self):
        print("activate_license test_employee_not_found_for_user Test license activation when employee is not found for the user")
        user_without_employee = User.objects.create_user(username='noemployee', password='pass')
        token_no_employee = str(AccessToken.for_user(user_without_employee))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_no_employee)
        payload = {"license_type": self.license_type_monthly.id}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
