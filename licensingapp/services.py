from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import LicenseType, Company, Employee, CompanyLicense
from .serializers import LicenseTypeSerializer, CompanySerializer, UserSerializer, EmployeeSerializer, CompanyRegistrationSerializer, CompanyLicenseSerializer, CompanyLicenseDetailSerializer, CompanyLicenseIncreaseUsersSerializer, EmployeeLicenseCapacitySerializer, EmployeeRegistrationByAdminSerializer, EmployeeGetSerializer
from django.db import transaction
from django.utils import timezone
import datetime
import logging
from project.commons.common_constants import Role

from project.commons.common_methods import paginatedResponse

logger = logging.getLogger(__name__)


class LicensingService:
    def __init__(self):
        pass

    def create_license_type(self, request):
        name = request.data.get('name')
        if not name:
            return Response({"status": "error", "errors": {"name": ["This field is required."]}},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            license_type = LicenseType.objects.get(name=name)
            serializer = LicenseTypeSerializer(license_type)
            return Response({"license": [serializer.data], "status": "success", "message": "License already exists"},
                            status=status.HTTP_200_OK)
        except LicenseType.DoesNotExist:
            serializer = LicenseTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"license": [serializer.data], "status": "success"},
                                status=status.HTTP_201_CREATED)
            return Response({"status": "error", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def update_license_type(self, request, pk):
        try:
            license_type = LicenseType.objects.get(pk=pk)
        except LicenseType.DoesNotExist:
            return Response({"status": "error", "message": "License type not found"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = LicenseTypeSerializer(license_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "License type updated successfully", "status": "success"},
                            status=status.HTTP_200_OK)
        return Response({"status": "error", "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_license_type(self, pk):
        try:
            license_type = LicenseType.objects.get(pk=pk)
            serializer = LicenseTypeSerializer(license_type)
            return Response({"license": [serializer.data], "status": "success"}, status=status.HTTP_200_OK)
        except LicenseType.DoesNotExist:
            return Response({"status": "error", "message": "License type not found"},
                            status=status.HTTP_404_NOT_FOUND)

    def get_all_license_types(self):
        license_types = LicenseType.objects.all()
        serializer = LicenseTypeSerializer(license_types, many=True)
        return Response({"license_types": serializer.data, "status": "success"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def register_company(self, request):
        serializer = CompanyRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            created_objects = serializer.create(serializer.validated_data)

            if not created_objects or 'user' not in created_objects or 'company' not in created_objects:
                logger.error("Missing 'user' or 'company' in created objects: %s", created_objects)
                return Response({"status": "error", "message": "Failed to create user or company"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user_instance = created_objects['user']
            company_instance = created_objects['company']


            user_data = UserSerializer(user_instance).data
            company_data = CompanySerializer(company_instance).data

            response_data = {
                'user': user_data,
                'company': company_data
            }

            return Response({"message": "Company registered successfully", "status": "success", "data": response_data}, status=201)
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    def activate_license(self, request):
        license_type_id = request.data.get('license_type')
        user = request.user

        try:
            employee = Employee.objects.get(user=user)
            company = employee.company
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Employee not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        latest_license: CompanyLicense = CompanyLicense.objects.filter(company=company).order_by('-end_date').first()

        if not license_type_id and not latest_license:
            return Response({"status": "error", "message": "No previous license found for this company"}, status=status.HTTP_400_BAD_REQUEST)

        if latest_license:
            start_date = latest_license.end_date + datetime.timedelta(days=1)
            total_users = latest_license.total_users
        else:
            start_date = timezone.now().date()
            total_users = 1

        if license_type_id:
            try:
                license_type = LicenseType.objects.get(pk=license_type_id)
            except LicenseType.DoesNotExist:
                return Response({"status": "error", "message": "License type not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            license_type = latest_license.license_type


        duration = license_type.duration
        duration_type = license_type.duration_type

        if duration_type == 'days':
            end_date = start_date + datetime.timedelta(days=duration)
        elif duration_type == 'months':
            end_date = start_date + datetime.timedelta(days=30 * duration)
        elif duration_type == 'years':
            end_date = start_date + datetime.timedelta(days=365 * duration)
        else:
            return Response({"status": "error", "message": "Invalid duration type"}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = license_type.price_per_user * int(total_users)

        new_license = CompanyLicense.objects.create(
            company=company,
            license_type=license_type,
            total_users=total_users,
            total_amount=total_amount,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )

        serializer = CompanyLicenseDetailSerializer(new_license)
        return Response({"message": "License activated successfully", "status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def increase_total_users(self, request):
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            company = employee.company
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Employee not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        latest_license: CompanyLicense = CompanyLicense.objects.filter(company=company, status='active').order_by('-end_date').first()

        if not latest_license:
            return Response({"status": "error", "message": "No active license found for this company"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyLicenseIncreaseUsersSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        total_users_to_add = serializer.validated_data['total_users_to_add']

        latest_license.total_users += total_users_to_add
        latest_license.total_amount = latest_license.license_type.price_per_user * latest_license.total_users
        latest_license.save()

        response_serializer = CompanyLicenseDetailSerializer(latest_license)
        return Response({"message": "Total users increased successfully", "status": "success", "data": response_serializer.data}, status=status.HTTP_200_OK)

    def check_license_capacity(self, request):
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            company = employee.company
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Employee not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        current_employees_count = Employee.objects.filter(company=company).count()

        latest_license: CompanyLicense = CompanyLicense.objects.filter(company=company, status='active').order_by('-end_date').first()

        allowed_users = 0
        if latest_license:
            allowed_users = latest_license.total_users
        else:
            return Response({"status": "error", "message": "No active license found for this company"}, status=status.HTTP_404_NOT_FOUND)

        users_left = max(0, allowed_users - current_employees_count)

        data = {
            'current_employees': current_employees_count,
            'allowed_users': allowed_users,
            'users_left': users_left
        }
        serializer = EmployeeLicenseCapacitySerializer(data)
        return Response({"message": "License capacity details retrieved successfully", "status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @transaction.atomic
    def register_employee_by_admin(self, request):
        user = request.user
        try:
            admin_employee = Employee.objects.get(user=user)
            company = admin_employee.company
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Admin employee not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        capacity_response = self.check_license_capacity(request)
        if capacity_response.status_code != status.HTTP_200_OK or capacity_response.data.get('status') == 'error':
            return capacity_response

        capacity_data = capacity_response.data.get('data', {})
        users_left = capacity_data.get('users_left', 0)

        if users_left <= 0:
            return Response({"status": "error", "message": "No more capacity available for new employees on the current license."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmployeeRegistrationByAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_user = serializer.save()

            employee = Employee.objects.create(
                user=new_user,
                company=company,
                role=Role.USER.value
            )

            response_serializer = EmployeeSerializer(employee)
            return Response({"message": "Employee registered successfully", "status": "success", "data": response_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error registering employee: {e}")
            return Response({"status": "error", "message": "Failed to register employee.", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_company_employees(self, request):
        user = request.user
        try:
            admin_employee = Employee.objects.get(user=user)
            company = admin_employee.company
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Admin employee not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        offset = int(request.query_params.get('offset', 0))
        limit = int(request.query_params.get('limit', 10))

        first_name = request.query_params.get('first_name', None)
        last_name = request.query_params.get('last_name', None)
        username = request.query_params.get('username', None)

        employees = Employee.objects.filter(company=company)

        if first_name:
            employees = employees.filter(user__first_name__icontains=first_name)
        if last_name:
            employees = employees.filter(user__last_name__icontains=last_name)
        if username:
            employees = employees.filter(user__username__icontains=username)

        total_count = employees.count()
        employees = employees[offset:offset + limit]

        serializer = EmployeeGetSerializer(employees, many=True)
        return paginatedResponse(offset, limit, total_count, serializer, 'employees')
    
    @transaction.atomic
    def delete_employee(self, request, pk):
        user = request.user
        try:
            admin_employee = Employee.objects.get(user=user)
            company = admin_employee.company
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Admin employee not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        try:
            employee_to_delete = Employee.objects.get(pk=pk, company=company)
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        if employee_to_delete == admin_employee:
            return Response({"status": "error", "message": "Not authorized to delete yourself"}, status=status.HTTP_403_FORBIDDEN)

        user_to_delete = User.objects.get(pk=employee_to_delete.user.id)

        employee_to_delete.delete()
        user_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def delete_company(self, request, pk):
        user = request.user
        try:
            admin_employee = Employee.objects.get(user=user)
            company_to_delete = Company.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Admin employee not found for this user"}, status=status.HTTP_403_FORBIDDEN)
        except Company.DoesNotExist:
            return Response({"status": "error", "message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        if admin_employee.role != Role.ADMIN.value:
            return Response({"status": "error", "message": "Only an admin can delete a company"}, status=status.HTTP_403_FORBIDDEN)

        if company_to_delete.id != admin_employee.company.id:
            return Response({"status": "error", "message": "Not authorized to delete other companies"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_ids_to_delete = list(Employee.objects.filter(company=company_to_delete).values_list('user__id', flat=True))

            CompanyLicense.objects.filter(company=company_to_delete).delete()

            Employee.objects.filter(company=company_to_delete).delete()

            User.objects.filter(id__in=user_ids_to_delete).delete()

            company_to_delete.delete()

            return Response({"message": "Company and all associated data deleted successfully", "status": "success"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting company (ID: {pk}): {e}")
            return Response({"status": "error", "message": "An error occurred during company deletion", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_company_license_info(self, request):
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            company = employee.company
        except Employee.DoesNotExist:
            return Response({"status": "error", "message": "Employee not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        company_serializer = CompanySerializer(company)

        active_license = CompanyLicense.objects.filter(
            company=company,
            status='active',
            end_date__gte=timezone.now().date()
        ).order_by('-end_date').first()

        license_data = None
        if active_license:
            license_data = CompanyLicenseDetailSerializer(active_license).data

        response_data = {
            "company": company_serializer.data,
            "active_license": license_data
        }

        return Response({"message": "Company and license info retrieved successfully", "status": "success", "data": response_data}, status=status.HTTP_200_OK)

    @transaction.atomic
    def register_company_for_existing_user(self, request):
        user = request.user

        if Employee.objects.filter(user=user).exists():
            return Response({"status": "error", "message": "User is already associated with a company."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            try:
                company_instance = serializer.save()

                employee_instance = Employee.objects.create(
                    user=user,
                    company=company_instance,
                    role=Role.ADMIN.value
                )

                response_data = {
                    'company': CompanySerializer(company_instance).data,
                    'employee': EmployeeSerializer(employee_instance).data
                }

                return Response({"message": "Company registered successfully for existing user", "status": "success", "data": response_data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error registering company for existing user: {e}")
                return Response({"status": "error", "message": "Failed to register company.", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)