from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import Company, Employee, CompanyLicense, LicenseType
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from project.commons.common_constants import Role
import datetime
from django.utils import timezone

class DeleteCompanyTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin_main', password='adminpassword')
        self.admin_company = Company.objects.create(name='Main Company', address='123 Main St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.employee_user = User.objects.create_user(username='employee_main', password='employeepass')
        self.employee_main = Employee.objects.create(user=self.employee_user, company=self.admin_company, role=Role.USER.value)

        self.license_type = LicenseType.objects.create(
            name='Standard', price_per_user=10.00, duration=1, duration_type='months'
        )
        self.company_license = CompanyLicense.objects.create(
            company=self.admin_company, license_type=self.license_type,
            total_users=5, total_amount=50.00,
            start_date=timezone.now().date(), end_date=timezone.now().date() + datetime.timedelta(days=30),
            status='active'
        )

        self.delete_url = reverse('delete-company', args=[self.admin_company.id])

        self.other_company_admin_user = User.objects.create_user(username='admin_other', password='otheradminpass')
        self.other_company = Company.objects.create(name='Other Company', address='456 Other St')
        self.other_company_admin_employee = Employee.objects.create(user=self.other_company_admin_user, company=self.other_company, role=Role.ADMIN.value)
        self.other_company_admin_access_token = str(AccessToken.for_user(self.other_company_admin_user))

        self.non_admin_user = User.objects.create_user(username='nonadmin', password='nonadminpass')
        Employee.objects.create(user=self.non_admin_user, company=self.admin_company, role=Role.USER.value)
        self.non_admin_access_token = str(AccessToken.for_user(self.non_admin_user))


    def test_success_company_deletion_by_its_admin(self):
        initial_company_count = Company.objects.count()
        initial_employee_count = Employee.objects.count()
        initial_user_count = User.objects.count()
        initial_license_count = CompanyLicense.objects.count()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.delete(self.delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Company.objects.filter(id=self.admin_company.id).exists())
        self.assertFalse(Employee.objects.filter(company=self.admin_company).exists())
        self.assertFalse(User.objects.filter(id=self.admin_user.id).exists())
        self.assertFalse(User.objects.filter(id=self.employee_user.id).exists())
        self.assertFalse(User.objects.filter(id=self.non_admin_user.id).exists())
        self.assertFalse(CompanyLicense.objects.filter(company=self.admin_company).exists())

        self.assertEqual(Company.objects.count(), initial_company_count - 1)
        self.assertEqual(Employee.objects.count(), initial_employee_count - 3)
        self.assertEqual(User.objects.count(), initial_user_count - 3)
        self.assertEqual(CompanyLicense.objects.count(), initial_license_count - 1)


    def test_company_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        non_existent_id = self.admin_company.id + 999
        url = reverse('delete-company', args=[non_existent_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "Company not found")

    def test_unauthenticated(self):
        self.client.credentials()
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin_role(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.non_admin_access_token)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_admin_employee_not_found(self):
        user_without_employee = User.objects.create_user(username='noemployee_user', password='pass')
        token_no_employee = str(AccessToken.for_user(user_without_employee))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_no_employee)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_admin_deletes_other_company(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_company_admin_access_token)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "Not authorized to delete other companies")

        self.assertTrue(Company.objects.filter(id=self.admin_company.id).exists())
        self.assertTrue(Employee.objects.filter(company=self.admin_company).exists())
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())
        self.assertTrue(User.objects.filter(id=self.employee_user.id).exists())
        self.assertTrue(CompanyLicense.objects.filter(company=self.admin_company).exists())