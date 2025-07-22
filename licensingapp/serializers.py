from rest_framework import serializers
from django.contrib.auth.models import User
from .models import LicenseType, Company, Employee, CompanyLicense


class LicenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseType
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Employee
        fields = ['id', 'user', 'company', 'role']


class EmployeeGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'company', 'role']


class CompanyRegistrationSerializer(serializers.Serializer):
    user = UserSerializer()
    company = CompanySerializer()

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        company_data = validated_data.pop('company')

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        company_serializer = CompanySerializer(data=company_data)
        company_serializer.is_valid(raise_exception=True)
        company = Company.objects.create(**company_serializer.validated_data)

        Employee.objects.create(user=user, company=company, role='admin')

        return {'user': user, 'company': company}


class CompanyLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLicense
        fields = '__all__'


class CompanyLicenseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLicense
        fields = '__all__'
        depth = 1
        
class CompanyLicenseIncreaseUsersSerializer(serializers.Serializer):
    total_users_to_add = serializers.IntegerField(min_value=1)


class EmployeeLicenseCapacitySerializer(serializers.Serializer):
    current_employees = serializers.IntegerField()
    allowed_users = serializers.IntegerField()
    users_left = serializers.IntegerField()


class EmployeeRegistrationByAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}