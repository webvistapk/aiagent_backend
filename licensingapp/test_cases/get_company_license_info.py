from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import Company, Employee, CompanyLicense, LicenseType
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from project.commons.common_constants import Role
import datetime
from django.utils import timezone

class GetCompanyLicenseInfoTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin_main', password='adminpassword')
        self.admin_company = Company.objects.create(name='Main Company', address='123 Main St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.license_type = LicenseType.objects.create(
            name='Standard', price_per_user=10.00, duration=1, duration_type='months'
        )
        # Active license
        self.active_company_license = CompanyLicense.objects.create(
            company=self.admin_company, license_type=self.license_type,
            total_users=5, total_amount=50.00,
            start_date=timezone.now().date(), end_date=timezone.now().date() + datetime.timedelta(days=30),
            status='active'
        )
        # Expired license (for testing no active license scenario)
        self.expired_company_license = CompanyLicense.objects.create(
            company=self.admin_company, license_type=self.license_type,
            total_users=3, total_amount=30.00,
            start_date=timezone.now().date() - datetime.timedelta(days=60),
            end_date=timezone.now().date() - datetime.timedelta(days=30),
            status='expired'
        )

        self.get_url = reverse('get-company-license-info')

        self.non_admin_user = User.objects.create_user(username='nonadmin', password='nonadminpass')
        Employee.objects.create(user=self.non_admin_user, company=self.admin_company, role=Role.USER.value)
        self.non_admin_access_token = str(AccessToken.for_user(self.non_admin_user))

        self.user_without_employee = User.objects.create_user(username='noemployee_user', password='pass')
        self.token_no_employee = str(AccessToken.for_user(self.user_without_employee))

        # Company with no active license
        self.company_no_active_license = Company.objects.create(name='Company No Active License', address='789 No License Ave')
        self.admin_no_active_license_user = User.objects.create_user(username='admin_no_license', password='adminpass')
        Employee.objects.create(user=self.admin_no_active_license_user, company=self.company_no_active_license, role=Role.ADMIN.value)
        self.token_admin_no_active_license = str(AccessToken.for_user(self.admin_no_active_license_user))

    def test_success_with_active_license(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.get(self.get_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('company', response.data['data'])
        self.assertIn('active_license', response.data['data'])

        company_data = response.data['data']['company']
        self.assertEqual(company_data['id'], self.admin_company.id)
        self.assertEqual(company_data['name'], self.admin_company.name)

        license_data = response.data['data']['active_license']
        self.assertIsNotNone(license_data)
        self.assertEqual(license_data['id'], self.active_company_license.id)
        self.assertEqual(license_data['status'], 'active')

    def test_success_no_active_license(self):
        print("\nTest successful retrieval when no active license")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_admin_no_active_license)
        response = self.client.get(self.get_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn('company', response.data['data'])
        self.assertIn('active_license', response.data['data'])

        company_data = response.data['data']['company']
        self.assertEqual(company_data['id'], self.company_no_active_license.id)
        self.assertEqual(company_data['name'], self.company_no_active_license.name)

        license_data = response.data['data']['active_license']
        self.assertIsNone(license_data)

    def test_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin_role(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.non_admin_access_token)
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_admin_employee_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_no_employee)
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "Employee not found for this user")