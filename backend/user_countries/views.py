from rest_framework import generics, viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.http import HttpResponse

import json

from .permissions.UserCountriesReadPermission import UserCountriesReadPermission

from .serializers import UserCountrySerializer

from country_list import countries_for_language

class UserCountriesView(viewsets.GenericViewSet,
                        mixins.ListModelMixin,):

    queryset = [{"value": value, "label": label} for (value, label) in dict(countries_for_language('en')).items()]
    authentication_classes = []
    permission_classes = [UserCountriesReadPermission]

    serializer_class = UserCountrySerializer

    def list(self, request):
        return HttpResponse(json.dumps(self.queryset), content_type="application/json")

    def get_queryset(self):
        return self.queryset