from django.db.models import Q
from django.contrib.auth.models import Permission

def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return Permission.objects.filter(Q(group__in=user.groups.all())|Q(user=user)).distinct()