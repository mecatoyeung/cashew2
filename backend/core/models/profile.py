"""
Database models.
"""

from datetime import datetime

from django.db import models

from django.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)

from django.utils.crypto import get_random_string, salted_hmac

from django.contrib.auth.models import User

from country_list import countries_for_language


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.TextField(max_length=1023, blank=False)
    company_name = models.TextField(max_length=1023, blank=True)
    country = models.CharField(
        max_length=1023,
        choices=[value for (value, label) in dict(
            countries_for_language('en')).items()],
        blank=True)
