from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

class UserManagementPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.has_perm("cashew_user_management"):
            return True
        return False