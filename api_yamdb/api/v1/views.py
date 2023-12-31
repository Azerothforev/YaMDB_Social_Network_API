from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .permissions import (
    DeleteGetPatchPermission,
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrReadOnly)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserSignUpSerializer,
    UsersSerializer,
    UsersSerializerAdmin)
from reviews.models import Category, Genre, Review, Title, User

CONFIRM_CODE_LENGTH: str = 32
EMAIL_FROM_ADDRESS: str = 'YaMDB@yandex.ru'
EMAIL_FROM_SUBJECT: str = 'YaMDB registration'
EMAIL_MESSAGE_REGISTER: str = (
    'Добро пожаловать на YaMDB - самый лучший сайт по предоставлению народных '
    'рецензий на книги, музыку, фильмы и многое другое!\n\nДля получения '
    'доступа к сайту, пожалуйста, отправьте POST запрос на адрес '
    'http://127.0.0.1:8000/api/v1/auth/token/ для получения JWT-токена.\n\n'
    'Обращаем ваше внимание, что в теле запроса необходимо использовать '
    'следующий confirmation code (без кавычек):\n"{}"\n\nДанное письмо было '
    'сформировано автоматически, пожалуйста, не отвечайте на его.\n\nЕсли Вы '
    'не указывали свою почту для регистрации на сайте YaMDB, пожалуйста, '
    'проигнорируйте это сообщение.')
EMAIL_MESSAGE_RESTORE: str = (
    'Здравствуйте,\n\nВы получили это письмо, потому что запросили '
    'восстановление доступа к сайту YaMDB.\n\nНапоминаем Вам, что для '
    'получения доступа необходимо отправить POST запрос на адрес '
    'http://127.0.0.1:8000/api/v1/auth/token/ для получения JWT-токена.\n\n'
    'Обращаем ваше внимание, что в теле запроса необходимо использовать '
    'следующий confirmation code (без кавычек):\n"{}"\n\nДанное письмо было '
    'сформировано автоматически, пожалуйста, не отвечайте на его.\n\nЕсли Вы '
    'не указывали свою почту для регистрации на сайте YaMDB, пожалуйста, '
    'проигнорируйте это сообщение.')


class CreateDestroyList(
        GenericViewSet, CreateModelMixin, DestroyModelMixin, ListModelMixin):
    """Класс-шаблон для GET(list), POST, DELETE запросов."""
    pass


@api_view(('POST',))
def auth_signup(request):
    """Производит регистрацию нового пользователя. Отправляет электронное
    письмо с confirmation_code для получения JWT access token'a.
    """
    serializer = UserSignUpSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user, created = User.objects.get_or_create(
        username=serializer.data['username'],
        email=serializer.data['email'])
    if not created:
        message = EMAIL_MESSAGE_RESTORE.format(user.confirmation_code)
    else:
        confirmation_code = default_token_generator.make_token(user=user)
        user.confirmation_code = confirmation_code
        user.save()
        message = EMAIL_MESSAGE_REGISTER.format(confirmation_code)
    send_mail(
        from_email=EMAIL_FROM_ADDRESS,
        message=message,
        recipient_list=[user.email],
        subject=EMAIL_FROM_SUBJECT)
    return Response(serializer.data, status=status.HTTP_200_OK)


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


class CategoryViewSet(CreateDestroyList):
    """Для любого пользователя позволяет получить список всех категорий.
    Для пользователя с уровнем прав не менее "admin" позволяет создать или
    удалить категорию по slug полю.
    """
    filter_backends = (SearchFilter,)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CommentViewSet(ModelViewSet):
    """Для любого пользователя позволяет получить список всех комментариев к
    отзыву или какого-то определенного по id.
    Для пользователя с уровнем прав не менее "user" позволяет создать
    комментариев к любому отзыву.
    Для пользователя с уровнем прав не менее "moderator" или автору позволяет
    частично обновить или удалить комментарий по id.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def __get_review(self, get_data):
        return get_object_or_404(Review, pk=get_data.get('review_id'))

    def get_queryset(self):
        return self.__get_review(get_data=self.kwargs).comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.__get_review(get_data=self.kwargs))


class GenreViewSet(CreateDestroyList):
    """Для любого пользователя позволяет получить список всех жанров.
    Для пользователя с уровнем прав не менее "admin" позволяет создать или
    удалить жанр по slug полю.
    """
    filter_backends = (SearchFilter,)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class TitleViewSet(ModelViewSet):
    """Для любого пользователя позволяет получить список всех произведений
    или информацию о конкретном произведении.
    Для пользователя с уровнем прав не менее "admin" позволяет создать,
    частично обновить или удалить произведение по id.
    """
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TitleSerializer
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))


class ReviewViewSet(ModelViewSet):
    """Для любого пользователя позволяет получить список всех отзывов к
    произведению или какого-то определенного по id.
    Для пользователя с уровнем прав не менее "user" позволяет создать
    отзыв к любому произведению.
    Для пользователя с уровнем прав не менее "moderator" или автору позволяет
    частично обновить или удалить отзыв по id.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        title_queryset = title.reviews.all()
        return title_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class UsersViewSet(ModelViewSet):
    """Для пользователя с уровнем прав не менее "user", позволяет получить
    или частично изменить свои данные (кроме значения поля "role").
    Для пользователя с уровнем прав не менее "admin" позволяет получить
    список всех пользователей или создать нового, а также получить, изменить
    или удалить данные любого пользователя по username.
    """
    filter_backends = (SearchFilter,)
    http_method_names = ('delete', 'get', 'patch', 'post')
    lookup_field = 'username'
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
