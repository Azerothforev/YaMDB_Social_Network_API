from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
import random
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
import string

from reviews.models import User
from .permissions import DeleteGetPatchPermission, IsAdmin
from .serializers import (
    UserSignUpSerializer,
    UsersSerializer,
    UsersSerializerAdmin)

CONFIRM_CODE_LENGTH: str = 32
EMAIL_FROM: str = 'YaMDB@yandex.ru'
EMAIL_SBJ: str = 'YaMDB registration successful!'
EMAIL_MESSAGE: str = (
    'Добро пожаловать на YaMDB - самый лучший сайт по предоставлению народных '
    'рецензий на книги, музыку, фильмы и многое другое!\n\nДля получения '
    'доступа к сайту, пожалуйста, отправьте POST запрос на адрес '
    'http://127.0.0.1:8000/api/v1/auth/token/ для получения JWT-токена.\n\n'
    'Обращаем ваше внимание, что в теле запроса необходимо использовать '
    'следующий confirmation code (без кавычек):\n"{}"')


def generate_confirmation_code() -> str:
    """Генерирует случайную последовательность символов."""
    chars: str = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(CONFIRM_CODE_LENGTH))


def send_email(confirmation_code: str, address: str) -> True:
    """Отправляет сообщение с заданным текстом на указанный почтовый адрес."""
    send_mail(
        subject=EMAIL_SBJ,
        message=EMAIL_MESSAGE.format(confirmation_code),
        from_email=EMAIL_FROM,
        recipient_list=[address])
    return True


class AuthSignupViewSet(GenericViewSet, CreateModelMixin):
    """Производит регистрацию нового пользователя. Отправляет электронное
    письмо с confirmation_code для получения JWT access token'a.
    """
    serializer_class = UserSignUpSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        if 'username' in request.data and 'email' in request.data:
            if request.data['username'] == 'me':
                err = {"username": ["Username is invalid."]}
                return Response(err, status=status.HTTP_400_BAD_REQUEST)
            elif self.queryset.filter(
                    username=request.data['username'],
                    email=request.data['email']).exists():
                return Response(
                    User.objects.get(
                        username=request.data['username']).confirmation_code,
                    status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = generate_confirmation_code()
        message = send_email(
            confirmation_code=confirmation_code,
            address=serializer.validated_data['email'])
        if message:
            serializer.save(confirmation_code=confirmation_code)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK)
        else:
            err = {"Server error": ["Please, come back and try again later!"]}
            return Response(err, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(('POST',))
def AuthToken(request):
    """Производит выдачу JWT-токена взамен username и confirmation code."""
    err: dict = {}
    for key in ('username', 'confirmation_code'):
        if key not in request.data:
            err[f"{key}"] = ["This field is required."]
    if err:
        return Response(err, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, username=request.data['username'])
    if user.confirmation_code != request.data['confirmation_code']:
        err = {"confirmation_code": ["Confirmation_code is invalid."]}
        return Response(err, status=status.HTTP_400_BAD_REQUEST)
    access_token = {'token': str(RefreshToken.for_user(user).access_token)}
    return Response(access_token, status=status.HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    """Для пользователя с уровнем прав не менее "user", позволяет получить
    или частично изменить свои данные (кроме значения поля "role").
    Для пользователя с уровнем прав не менее "admin" позволяет получить
    список всех пользователей или создать нового, а также получить, изменить
    или удалить данные любого пользователя по username.
    """
    filter_backends = (SearchFilter,)
    http_method_names = ('delete', 'get', 'patch', 'post')
    lookup_field = "username"
    permission_classes = (IsAdmin,)
    search_fields = ('username',)
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.path == '/api/v1/users/me/':
            serializer = UsersSerializer
        else:
            serializer = UsersSerializerAdmin
        return serializer

    @action(
        detail=False,
        methods=('get', 'patch'),
        url_path='me',
        permission_classes=(IsAuthenticated, DeleteGetPatchPermission))
    def users_me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            serializer = UsersSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UsersSerializer(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            serializer = UsersSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
