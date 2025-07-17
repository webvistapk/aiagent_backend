from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from licensingapp.models import Employee

class AdminRoleCheckPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            try:
                employee = Employee.objects.get(user=request.user)
                if employee.role == 'admin':
                    return True  # User has admin role, proceed to view
                else:
                    return False # User does not have admin role
            except Employee.DoesNotExist:
                return False # Employee not found
        return False  # Authentication required