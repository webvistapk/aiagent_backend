from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import LicenseType, Company, Employee
from .serializers import LicenseTypeSerializer, CompanySerializer, UserSerializer, EmployeeSerializer, CompanyRegistrationSerializer
from django.db import transaction


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

    @transaction.atomic
    def register_company(self, request):
        serializer = CompanyRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.create(serializer.validated_data)
            user = User.objects.get(username=serializer.data['user']['username']) # get user object by username
            company = Company.objects.get(name=serializer.data['company']['name']) # get company object by name
            user_data = UserSerializer(user).data
            company_data = CompanySerializer(company).data

            response_data = {
                'user': user_data,
                'company': company_data
            }

            return Response({"message": "Company registered successfully", "status": "success", "data": response_data}, status=201)
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=400)