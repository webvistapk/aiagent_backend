from rest_framework.test import APITestCase
from django.urls import reverse
from licensingapp.models import Company, Employee
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from project.commons.common_constants import Role

class DeleteEmployeeTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_company = Company.objects.create(name='Admin Company', address='123 Admin St')
        self.admin_employee = Employee.objects.create(user=self.admin_user, company=self.admin_company, role=Role.ADMIN.value)
        self.admin_access_token = str(AccessToken.for_user(self.admin_user))

        self.employee_to_delete_user = User.objects.create_user(username='todelete', password='deletepass')
        self.employee_to_delete = Employee.objects.create(user=self.employee_to_delete_user, company=self.admin_company, role=Role.USER.value)
        self.delete_url = reverse('delete-employee', args=[self.employee_to_delete.id])

        self.other_company = Company.objects.create(name='Other Company', address='456 Other St')
        self.employee_other_company_user = User.objects.create_user(username='othercompanyemp', password='otherpass')
        self.employee_other_company = Employee.objects.create(user=self.employee_other_company_user, company=self.other_company, role=Role.USER.value)

    def test_success(self):
        print("Test successful employee deletion by admin")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Employee.objects.filter(id=self.employee_to_delete.id).exists())
        self.assertFalse(User.objects.filter(id=self.employee_to_delete_user.id).exists())

    def test_employee_not_found(self):
        print("Test delete non-existent employee")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        non_existent_id = self.employee_to_delete.id + 999
        url = reverse('delete-employee', args=[non_existent_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "Employee not found")

    def test_delete_employee_from_other_company(self):
        print("Test delete employee from another company")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        url = reverse('delete-employee', args=[self.employee_other_company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "Employee not found")
        self.assertTrue(Employee.objects.filter(id=self.employee_other_company.id).exists()) # Should not be deleted

    def test_delete_self(self):
        print("Test admin attempts to delete their own account")
        self_delete_url = reverse('delete-employee', args=[self.admin_employee.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.delete(self_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['status'], "error")
        self.assertEqual(response.data['message'], "Not authorized to delete yourself")
        self.assertTrue(Employee.objects.filter(id=self.admin_employee.id).exists()) # Should not be deleted

    def test_unauthenticated(self):
        print("Test delete employee without authentication")
        self.client.credentials() # Clear credentials
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin(self):
        print("Test delete employee by a non-admin user")
        non_admin_user = User.objects.create_user(username='regularuser', password='userpassword')
        Employee.objects.create(user=non_admin_user, company=self.admin_company, role=Role.USER.value)
        non_admin_access_token = str(AccessToken.for_user(non_admin_user))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + non_admin_access_token)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_admin_employee_not_found(self):
        print("Test delete employee when admin employee is not found for the user (user exists but no employee obj)")
        user_without_employee = User.objects.create_user(username='noemployee', password='pass')
        token_no_employee = str(AccessToken.for_user(user_without_employee))

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_no_employee)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
