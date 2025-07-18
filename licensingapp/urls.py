from django.urls import path
from .views import *

urlpatterns = [
    path('types/create/', create_license_type, name='create-license-type'),
    path('types/update/<int:pk>/', update_license_type, name='update-license-type'),
    path('types/get/<int:pk>/', get_license_type, name='get-license-type'),
    path('types/all/', get_all_license_types, name='get-all-license-types'),
    path('company/register/', register_company, name='register-company'),
    path('license/activate/', activate_license, name='activate-license'),
]