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
]