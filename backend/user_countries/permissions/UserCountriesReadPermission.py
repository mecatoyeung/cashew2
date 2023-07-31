from rest_framework import permissions

class UserCountriesReadPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print(request)
        return True

    def has_object_permission(self, request, view, obj):
        print(request)
        return True