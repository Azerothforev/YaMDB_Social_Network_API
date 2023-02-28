from django.core.mail import send_mail
import random
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
import string

from reviews.models import User
from .serializers import UserSignUpSerializer

EMAIL_TEXT_SBJ = 'YaMDB'
EMAIL_TEXT: str = (
    'Добро пожаловать на YaMDB - самый лучший сайт по предоставлению народных '
    'рецензий на книги, музыку, фильмы и многое другое!\n\nДля получения '
    'доступа к сайту, пожалуйста, отправьте POST запрос на адрес '
    'http://127.0.0.1:8000/api/v1/auth/token/ для получения JWT-токена.\n\n'
    'Обращаем ваше внимание, что в теле запроса необходимо использовать '
    'следующий confirmation code (без кавычек):\n"{}"')


def generate_confirmation_code() -> str:
    """Генерирует случайную последовательность символов."""
    LENGTH: str = 32
    chars: str = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(LENGTH))


def send_email(confirmation_code: str, address: str) -> True:
    """Отправляет сообщение с заданным текстом на указанный почтовый адрес."""
    send_mail(
        subject=EMAIL_TEXT_SBJ,
        message=EMAIL_TEXT.format(confirmation_code),
        from_email='YaMDB@yandex.ru',
        recipient_list=[address])
    return True


class AuthSignupViewSet(CreateModelMixin, GenericViewSet):
    """Производит регистрацию нового пользователя. Отправляет электронное
    письмо с confirmation_code для получения JWT access token'a.
    """
    serializer_class = UserSignUpSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        confirmation_code = generate_confirmation_code()
        send_email(
            confirmation_code=confirmation_code,
            address=serializer.validated_data['email'])
        return serializer.save(confirmation_code=confirmation_code)


class AuthTokenViewSet(CreateModelMixin, GenericViewSet):
    """Производит выдачу JWT access токена."""
    pass
