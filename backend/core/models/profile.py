from django.db import models

from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.TextField(max_length=1023, blank=False)
    company_name = models.TextField(max_length=1023, blank=True)
    country = models.CharField(
        max_length=1023,
        blank=True)

