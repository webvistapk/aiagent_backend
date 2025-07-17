from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services import LicensingService
from .serializers import LicenseTypeSerializer, CompanySerializer, CompanyRegistrationSerializer

from project.commons.common_methods import get_serializer_schema

licensing_service = LicensingService()


@swagger_auto_schema(
    method='post', operation_id="create_license_type", request_body=LicenseTypeSerializer,
    responses={200: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'license': openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(
                        type=openapi.TYPE_OBJECT, properties=get_serializer_schema(LicenseTypeSerializer),
                    ),
                ),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
            },
        ),
    ),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_license_type(request: Request) -> Response:
    return licensing_service.create_license_type(request)


@swagger_auto_schema(
    method='patch', operation_id="update_license_type", request_body=LicenseTypeSerializer, responses={200: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
            },
        ),
    ),
    },
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_license_type(request: Request, pk: int) -> Response:
    return licensing_service.update_license_type(request, pk)


@swagger_auto_schema(
    method='get', operation_id="get_license_type", responses={200: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'license': openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(
                        type=openapi.TYPE_OBJECT, properties=get_serializer_schema(LicenseTypeSerializer),
                    ),
                ),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
            },
        ),
    ),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_license_type(request: Request, pk: int) -> Response:
    return licensing_service.get_license_type(pk)


@swagger_auto_schema(
    method='post', operation_id="register_company", request_body=CompanyRegistrationSerializer,
    responses={201: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'data': openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(
                        type=openapi.TYPE_OBJECT, properties=get_serializer_schema(CompanyRegistrationSerializer),
                    ),
                ),
            },
        ),
    ),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_company(request: Request) -> Response:
    return licensing_service.register_company(request)
