from django.contrib.auth.models import User, Group, Permission

from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

class ParserManagementPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.has_perm("parsers.cashew_parser_management"):
            return True
        if request.method == "GET":
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method == "GET":
            return True
        else:
            if request.user.has_perm("parsers.cashew_parser_management"):
                if obj.owner.id == request.user.id:
                    return True
                for permitted_user in obj.permitted_users.all():
                    if permitted_user.id == request.user.id:
                        return True
                for permitted_group in obj.permitted_groups.all():
                    users = User.objects.filter(groups__id=permitted_group.id)
                    for user in users:
                        if user.id == request.user.id:
                            return True
        return False