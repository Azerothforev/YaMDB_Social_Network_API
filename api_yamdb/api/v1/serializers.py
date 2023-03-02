from rest_framework.serializers import ModelSerializer

from reviews.models import User


class UserSignUpSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')


class UsersSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)
