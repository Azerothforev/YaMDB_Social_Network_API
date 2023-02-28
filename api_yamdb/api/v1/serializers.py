from rest_framework.serializers import ModelSerializer

from reviews.models import User


class UserSignUpSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')


class UserTokenSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
