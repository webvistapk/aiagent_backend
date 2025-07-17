from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services import LicensingService
from .serializers import LicenseTypeSerializer

licensing_service = LicensingService()

@swagger_auto_schema(method='post', request_body=LicenseTypeSerializer, responses={201: LicenseTypeSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_license_type(request: Request) -> Response:
    return licensing_service.create_license_type(request)

@swagger_auto_schema(method='patch', request_body=LicenseTypeSerializer, responses={200: LicenseTypeSerializer})
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_license_type(request: Request, pk: int) -> Response:
    return licensing_service.update_license_type(request, pk)

@swagger_auto_schema(method='get', responses={200: LicenseTypeSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_license_type(request: Request, pk: int) -> Response:
    return licensing_service.get_license_type(pk)