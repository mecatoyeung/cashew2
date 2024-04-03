from rest_framework.permissions import BasePermission

class ParserManagementPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if request.user.is_superuser:
            return True
        if request.user.has_perm('cashew_parser_management'):
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        if request.user.is_superuser:
            return True
        if request.user.has_perm('cashew_parser_management'):
            return True
        return False