from django.urls import path
from .views import *

urlpatterns = [
    path('types/', create_license_type, name='create-license-type'),
    path('types/<int:pk>/', update_license_type, name='update-license-type'),
    path('types/<int:pk>/', get_license_type, name='get-license-type'),
]