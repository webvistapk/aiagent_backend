from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import LicenseType, Company, Employee, CompanyLicense
from .serializers import LicenseTypeSerializer, CompanySerializer, UserSerializer, EmployeeSerializer, CompanyRegistrationSerializer, CompanyLicenseSerializer, CompanyLicenseDetailSerializer, CompanyLicenseIncreaseUsersSerializer
from django.db import transaction
from django.utils import timezone
import datetime
import logging

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