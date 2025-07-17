from django.urls import path
from . import views

urlpatterns = [
    path('license-types/', views.create_license_type, name='create-license-type'),
    path('license-types/<int:pk>/', views.update_license_type, name='update-license-type'),
    path('license-types/<int:pk>/', views.get_license_type, name='get-license-type'),
]