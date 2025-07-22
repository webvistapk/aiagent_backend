from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from project.commons.middleware import AdminRoleCheckPermission

from .services import LicensingService
from .serializers import LicenseTypeSerializer, CompanySerializer, CompanyRegistrationSerializer, CompanyLicenseSerializer, CompanyLicenseIncreaseUsersSerializer, CompanyLicenseDetailSerializer, EmployeeLicenseCapacitySerializer, EmployeeRegistrationByAdminSerializer, EmployeeSerializer, EmployeeGetSerializer
from .models import CompanyLicense, Employee


from project.commons.common_methods import get_serializer_schema, paginatedResponse

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
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='')
            },
        ),
    )}
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
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='')
            },
        ),
    )}
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
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='')
            },
        ),
    )}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_license_type(request: Request, pk: int) -> Response:
    return licensing_service.get_license_type(pk)


@swagger_auto_schema(
    method='get', operation_id="get_all_license_types", responses={200: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'license_types': openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(
                        type=openapi.TYPE_OBJECT, properties=get_serializer_schema(LicenseTypeSerializer),
                    ),
                ),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='')
            },
        ),
    )}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_license_types(request: Request) -> Response:
    return licensing_service.get_all_license_types()


@swagger_auto_schema(
    method='post', operation_id="register_company", request_body=CompanyRegistrationSerializer,
    responses={201: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties=get_serializer_schema(CompanyRegistrationSerializer),
                ),
            },
        ),
    )}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_company(request: Request) -> Response:
    return licensing_service.register_company(request)


@swagger_auto_schema(
    method='post', operation_id="activate_license", request_body=CompanyLicenseSerializer,
    responses={201: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties=get_serializer_schema(CompanyLicenseSerializer),
                ),
            },
        ),
    )}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def activate_license(request: Request) -> Response:
    return licensing_service.activate_license(request)


@swagger_auto_schema(
    method='post', operation_id="increase_total_users", request_body=CompanyLicenseIncreaseUsersSerializer,
    responses={200: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties=get_serializer_schema(CompanyLicenseDetailSerializer),
                ),
            },
        ),
    )}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def increase_total_users(request: Request) -> Response:
    return licensing_service.increase_total_users(request)


@swagger_auto_schema(
    method='get', operation_id="check_license_capacity",
    responses={200: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties=get_serializer_schema(EmployeeLicenseCapacitySerializer),
                ),
            },
        ),
    )}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def check_license_capacity(request: Request) -> Response:
    return licensing_service.check_license_capacity(request)


@swagger_auto_schema(
    method='post', operation_id="register_employee", request_body=EmployeeRegistrationByAdminSerializer,
    responses={201: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties=get_serializer_schema(EmployeeSerializer),
                ),
            },
        ),
    ),
    400: openapi.Response(
        description="No more capacity available or invalid input",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'errors': openapi.Schema(type=openapi.TYPE_OBJECT, additionalProperties=True, description='Validation errors')
            }
        )
    ),
    404: openapi.Response(
        description="Admin employee not found or other internal error",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def register_employee(request: Request) -> Response:
    return licensing_service.register_employee_by_admin(request)


@swagger_auto_schema(
    method='get', operation_id="get_company_employees", responses={200: openapi.Response(
        description="",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description=''),
                'employees': openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(
                        type=openapi.TYPE_OBJECT, properties=get_serializer_schema(EmployeeGetSerializer),
                    ),
                ),
                'total_count': openapi.Schema(type=openapi.TYPE_INTEGER, description=''),
                'has_next_page': openapi.Schema(type=openapi.TYPE_BOOLEAN, description=''),
                'next_offset': openapi.Schema(type=openapi.TYPE_INTEGER, description=''),
                'has_previous_page': openapi.Schema(type=openapi.TYPE_BOOLEAN, description=''),
                'previous_offset': openapi.Schema(type=openapi.TYPE_INTEGER, description='')
            },
        ),
    )}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def get_company_employees(request: Request) -> Response:
    return licensing_service.get_company_employees(request)


@swagger_auto_schema(
    method='delete', operation_id="delete_employee", responses={204: openapi.Response(
        description="No Content",
    ),
    404: openapi.Response(
        description="Employee not found or Admin employee not found",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    ),
    403: openapi.Response(
        description="Not authorized to delete this employee",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def delete_employee(request: Request, pk: int) -> Response:
    return licensing_service.delete_employee(request, pk)

@swagger_auto_schema(
    method='delete', operation_id="delete_company", responses={204: openapi.Response(
        description="No Content",
    ),
    404: openapi.Response(
        description="Company not found or Admin employee not found",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    ),
    403: openapi.Response(
        description="Not authorized to delete this company",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    ),
    500: openapi.Response(
        description="Internal Server Error",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'detail': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def delete_company(request: Request, pk: int) -> Response:
    return licensing_service.delete_company(request, pk)

@swagger_auto_schema(
    method='get', operation_id="get_company_license_info",
    responses={200: openapi.Response(
        description="Company and active license information retrieved successfully",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'company': openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=get_serializer_schema(CompanySerializer)
                        ),
                        'active_license': openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=get_serializer_schema(CompanyLicenseDetailSerializer), nullable=True
                        )
                    }
                )
            }
        )
    ),
    403: openapi.Response(
        description="Forbidden: Admin employee not found for this user or not authorized",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    ),
    404: openapi.Response(
        description="Not Found: Employee not found for this user",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, AdminRoleCheckPermission])
def get_company_license_info(request: Request) -> Response:
    return licensing_service.get_company_license_info(request)