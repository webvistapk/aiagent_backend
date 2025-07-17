from rest_framework import serializers
from .models import LicenseType

class LicenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseType
        fields = '__all__'