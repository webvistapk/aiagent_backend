from django.urls import path
from .views import *

urlpatterns = [
    path('types/create/', create_license_type, name='create-license-type'),
    path('types/update/<int:pk>/', update_license_type, name='update-license-type'),
    path('types/get/<int:pk>/', get_license_type, name='get-license-type'),
    path('types/all/', get_all_license_types, name='get-all-license-types'),
    path('company/register/', register_company, name='register-company'),
    path('license/activate/', activate_license, name='activate-license'),
    path('license/increase-users/', increase_total_users, name='increase-license-users'),
    path('license/capacity-check/', check_license_capacity, name='check-license-capacity'),
    path('employee/register/', register_employee, name='register-employee-by-admin'),
    path('employees/company/', get_company_employees, name='get-company-employees'),
    path('employee/delete/<int:pk>/', delete_employee, name='delete-employee'),
    path('company/delete/<int:pk>/', delete_company, name='delete-company'),
    path('company/license-info/', get_company_license_info, name='get-company-license-info'),
    path('company/register-for-existing-user/', register_company_for_existing_user_view, name='register-company-for-existing-user'),
    path('user/company-employee-info/', get_user_company_and_employee_info_view, name='get-user-company-employee-info'),
]