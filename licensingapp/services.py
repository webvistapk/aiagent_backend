from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import LicenseType, Company, Employee
from .serializers import LicenseTypeSerializer, CompanySerializer, UserSerializer, EmployeeSerializer


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

    def register_company(self, request):
        user_serializer = UserSerializer(data=request.data)
        company_serializer = CompanySerializer(data=request.data)

        if user_serializer.is_valid() and company_serializer.is_valid():
            user = user_serializer.save()

            company = Company.objects.create(
                name=company_serializer.validated_data['name'],
                address=company_serializer.validated_data['address']
            )

            employee = Employee.objects.create(
                user=user,
                company=company,
                role='admin'
            )

            return Response({"message": "Company registered successfully", "status": "success"},
                            status=status.HTTP_201_CREATED)
        else:
            errors = {}
            if not user_serializer.is_valid():
                errors['user'] = user_serializer.errors
            if not company_serializer.is_valid():
                errors['company'] = company_serializer.errors
            return Response({"status": "error", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)