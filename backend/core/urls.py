from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from core.views.profile import ProfileViewSet
from core.views.user import UserViewSet


users_router = DefaultRouter()
users_router.register('', UserViewSet, basename="user")

profiles_router = DefaultRouter()
profiles_router.register('', ProfileViewSet, basename="profile")

app_name = "core"

urlpatterns = [
    #path('profiles/', include(profiles_router.urls), name="profiles"),
    path('users/', include(users_router.urls), name="users"),
    path('user/', UserViewSet.as_view(
        {"put": "partial_update", "get": "retrieve"}
    ), name="user-update")
]

