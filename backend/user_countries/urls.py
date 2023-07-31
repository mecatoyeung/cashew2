"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from user_countries import views


user_countries_router = DefaultRouter()
user_countries_router.register('', views.UserCountriesView, basename="user_countries")

app_name = "user_countries"

urlpatterns = [
    path('user_countries/', include(user_countries_router.urls), name="user_countries"),
]