from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from core.views.user import UserViewSet
from core.views.users import UsersViewSet
from core.views.group import GroupViewSet


users_router = DefaultRouter()
users_router.register('', UsersViewSet, basename="users")

groups_router = DefaultRouter()
groups_router.register('', GroupViewSet, basename="groups")

app_name = "core"

urlpatterns = [
    path('users/', include(users_router.urls), name="users"),
    path('user/', UserViewSet.as_view(
        {"put": "partial_update", "get": "retrieve"}
    ), name="user-update"),
    path('groups/', include(groups_router.urls), name="groups"),
]

