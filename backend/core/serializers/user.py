from rest_framework import serializers

from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

class UserCreateSerializer(UserSerializer):
    pass

class UserListSerializer(UserSerializer):
    pass

class UserRetrieveSerializer(UserSerializer):
    pass

class UserUpdateSerializer(UserSerializer):
    pass

class UserDeleteSerializer(UserSerializer):
    pass

