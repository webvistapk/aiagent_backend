from drf_yasg import openapi
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
        
def get_serializer_schema(serializer):
    """
    Extract fields from a serializer and return them as openapi.Schema format,
    handling different field types and nested serializers.
    """
    # Check if `serializer` is a class or an instance
    if isinstance(serializer, type):
        serializer_instance = serializer()  # Instantiate if it's a class
    else:
        serializer_instance = serializer  # Already an instance

    fields = serializer_instance.get_fields()
    properties = {}

    for field_name, field in fields.items():
        # Handle different types of fields
        if isinstance(field, serializers.CharField):
            field_type = openapi.TYPE_STRING
        elif isinstance(field, serializers.IntegerField):
            field_type = openapi.TYPE_INTEGER
        elif isinstance(field, serializers.BooleanField):
            field_type = openapi.TYPE_BOOLEAN
        elif isinstance(field, serializers.FloatField):
            field_type = openapi.TYPE_NUMBER
        elif isinstance(field, serializers.DateTimeField):
            field_type = openapi.TYPE_STRING  # or openapi.FORMAT_DATE_TIME
        elif isinstance(field, serializers.ListField):
            field_type = openapi.TYPE_ARRAY
            # Handle items in ListField, assuming it's a simple type or a nested serializer
            if isinstance(field.child, serializers.CharField):
                items = openapi.Schema(type=openapi.TYPE_STRING)
            elif isinstance(field.child, serializers.IntegerField):
                items = openapi.Schema(type=openapi.TYPE_INTEGER)
            elif isinstance(field.child, serializers.Serializer):
                items = openapi.Schema(type=openapi.TYPE_OBJECT, properties=get_serializer_schema(field.child))
            else:
                items = openapi.Schema(type=openapi.TYPE_OBJECT)  # Fallback
            properties[field_name] = openapi.Schema(type=openapi.TYPE_ARRAY, items=items)
            continue
        elif isinstance(field, serializers.Serializer):
            # Handle nested serializers
            field_type = openapi.TYPE_OBJECT
            properties[field_name] = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=get_serializer_schema(field.__class__)  # Recursively process nested serializer
            )
            continue
        else:
            field_type = openapi.TYPE_STRING  # Default type

        properties[field_name] = openapi.Schema(type=field_type)

    return properties

def paginatedResponse(offset, limit, total_count, serializer, result_type):
    has_next_page = (offset + limit) < total_count
    next_offset = offset + limit if has_next_page else None
    
    has_previous_page = offset > 0
    previous_offset = offset - limit if has_previous_page else None

    try:
        return Response({
            'status': "success",
            result_type: serializer.data,
            'total_count': total_count,
            'has_next_page': has_next_page,
            'next_offset': next_offset,
            'has_previous_page': has_previous_page,
            'previous_offset': previous_offset
        }, status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
