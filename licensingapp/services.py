from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import LicenseType, Company, Employee, CompanyLicense
from .serializers import LicenseTypeSerializer, CompanySerializer, UserSerializer, EmployeeSerializer, CompanyRegistrationSerializer, CompanyLicenseSerializer
from django.db import transaction
from django.utils import timezone
import datetime


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
            company = serializer.create(serializer.validated_data)
            user = User.objects.get(username=serializer.data['user']['username'])  # get user object by username
            company = Company.objects.get(name=serializer.data['company']['name'])  # get company object by name
            user_data = UserSerializer(user).data
            company_data = CompanySerializer(company).data

            response_data = {
                'user': user_data,
                'company': company_data
            }

            return Response({"message": "Company registered successfully", "status": "success", "data": response_data}, status=201)
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    def activate_license(self, request):
        company_id = request.data.get('company')
        license_type_id = request.data.get('license_type')
        total_users = request.data.get('total_users')

        if not company_id:
            return Response({"status": "error", "errors": {"message": ["company is required"]}},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({"status": "error", "message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the latest license for the company
        latest_license = CompanyLicense.objects.filter(company=company).order_by('-end_date').first()

        if not latest_license:
            return Response({"status": "error", "message": "No previous license found for this company"}, status=status.HTTP_400_BAD_REQUEST)

        if license_type_id:
            try:
                license_type = LicenseType.objects.get(pk=license_type_id)
            except LicenseType.DoesNotExist:
                return Response({"status": "error", "message": "License type not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Use the same license type as the previous license
            license_type = latest_license.license_type

        if total_users:
            total_users = int(total_users)
        else:
            # Use the same number of users as the previous license
            total_users = latest_license.total_users

        start_date = latest_license.end_date

        # Calculate end date based on license type
        duration = license_type.duration
        duration_type = license_type.duration_type

        if duration_type == 'days':
            end_date = start_date + datetime.timedelta(days=duration)
        elif duration_type == 'months':
            end_date = start_date + datetime.timedelta(days=30 * duration)  # Approximate months
        elif duration_type == 'years':
            end_date = start_date + datetime.timedelta(days=365 * duration)  # Approximate years
        else:
            return Response({"status": "error", "message": "Invalid duration type"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total amount
        total_amount = license_type.price_per_user * int(total_users)

        # Create new license
        new_license = CompanyLicense.objects.create(
            company=company,
            license_type=license_type,
            total_users=total_users,
            total_amount=total_amount,
            start_date=start_date,
            end_date=end_date,
            status='pending'  # Or set to 'active' directly if appropriate
        )

        serializer = CompanyLicenseSerializer(new_license)
        return Response({"message": "License activated successfully", "status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)