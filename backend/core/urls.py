from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from core.views.account import AccountViewSet
from core.views.users import UsersViewSet
from core.views.group import GroupViewSet
from core.views.permission import PermissionViewSet


account_router = DefaultRouter()
account_router.register('', AccountViewSet, basename="account")

permission_router = DefaultRouter()
permission_router.register('', PermissionViewSet, basename="account")

users_router = DefaultRouter()
users_router.register('', UsersViewSet, basename="users")

groups_router = DefaultRouter()
groups_router.register('', GroupViewSet, basename="groups")

app_name = "core"

urlpatterns = [
    path('account/', AccountViewSet.as_view({"put": "partial_update", "get": "retrieve"}), name="account-update"),
    path('account/', include(permission_router.urls), name="account"),
    path('users/', include(users_router.urls), name="users"),
    path('groups/', include(groups_router.urls), name="groups"),
]

