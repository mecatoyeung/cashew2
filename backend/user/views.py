"""
Views for the user API.
"""
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.settings import api_settings

from user.serializers import (
    UserCreateSerializer,
)

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.permissions import IsAdminUser

from rest_auth.registration.views import RegisterSerializer

