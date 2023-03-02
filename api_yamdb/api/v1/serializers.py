from rest_framework.serializers import ModelSerializer

from reviews.models import User


class UserSignUpSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')


class UsersSerializerAdmin(ModelSerializer):
    lookup_field = "username"

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class UsersSerializer(UsersSerializerAdmin):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)
