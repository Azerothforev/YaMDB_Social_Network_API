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
from rest_framework_simplejwt.tokens import AccessToken
import string

from reviews.models import User
from .permissions import DeleteGetPatchPermission, IsAdmin
from .serializers import (
    UserSignUpSerializer,
    UsersSerializer,
    UsersSerializerAdmin)

CONFIRM_CODE_LENGTH: str = 32
EMAIL_MESSAGE_REGISTER: str = (
    'Добро пожаловать на YaMDB - самый лучший сайт по предоставлению народных '
    'рецензий на книги, музыку, фильмы и многое другое!\n\nДля получения '
    'доступа к сайту, пожалуйста, отправьте POST запрос на адрес '
    'http://127.0.0.1:8000/api/v1/auth/token/ для получения JWT-токена.\n\n'
    'Обращаем ваше внимание, что в теле запроса необходимо использовать '
    'следующий confirmation code (без кавычек):\n"{}"\n\nДанное письмо было'
    'сформировано автоматически, пожалуйста, не отвечайте на его.\n\nЕсли Вы'
    'не указывали свою почту для регистрации на сайте YaMDB, пожалуйста, '
    'проигнорируйте это сообщение.')
EMAIL_MESSAGE_RESTORE: str = (
    'Здравствуйте,\n\nВы получили это письмо, потому что запросили '
    'восстановление доступа к сайту YaMDB.\n\nНапоминаем Вам, что для '
    'получения доступа необходимо отправить POST запрос на адрес '
    'http://127.0.0.1:8000/api/v1/auth/token/ для получения JWT-токена.\n\n'
    'Обращаем ваше внимание, что в теле запроса необходимо использовать '
    'следующий confirmation code (без кавычек):\n"{}"\n\nДанное письмо было'
    'сформировано автоматически, пожалуйста, не отвечайте на его.\n\nЕсли Вы'
    'не указывали свою почту для регистрации на сайте YaMDB, пожалуйста, '
    'проигнорируйте это сообщение.')


def generate_confirmation_code() -> str:
    """Генерирует случайную последовательность символов."""
    chars: str = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(CONFIRM_CODE_LENGTH))


def send_email(message: str, address: str) -> True:
    """Отправляет сообщение с заданным текстом на указанный почтовый адрес."""
    send_mail(
        subject='YaMDB registration',
        message=message,
        from_email='YaMDB@yandex.ru',
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
            try:
                user = User.objects.get(
                    username=request.data['username'],
                    email=request.data['email'])
                message = send_email(
                    message=EMAIL_MESSAGE_RESTORE.format(
                        user.confirmation_code),
                    address=user.email)
                if message:
                    return Response(request.data, status=status.HTTP_200_OK)
            except Exception:
                pass
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = generate_confirmation_code()
        message = send_email(
            message=EMAIL_MESSAGE_REGISTER.format(confirmation_code),
            address=serializer.validated_data['email'])
        if message:
            serializer.save(confirmation_code=confirmation_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            err = {"Server error": ["Please, come back and try again later!"]}
            return Response(err, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(('POST',))
def auth_token(request):
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
    access_token = {'token': str(AccessToken.for_user(user).access_token)}
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
    serializer_class = UsersSerializerAdmin
    queryset = User.objects.all()

    @action(
        detail=False,
        methods=('get', 'patch'),
        url_path='me',
        permission_classes=(IsAuthenticated, DeleteGetPatchPermission),
        serializer_class=UsersSerializer)
    def users_me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                serializer = self.get_serializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
