"""
URL mappings for the recipe app.
"""
import sys
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from core.views.profile import ProfileViewSet


profiles_router = DefaultRouter()
profiles_router.register('', ProfileViewSet, basename="profile")

app_name = "core"

urlpatterns = [
    path('profiles/', include(profiles_router.urls), name="profiles"),
]
