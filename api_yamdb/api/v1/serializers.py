from rest_framework.serializers import (
    EmailField,
    ModelSerializer,
    IntegerField,
    Serializer,
    SlugRelatedField,
    RegexField,
    ValidationError)

from reviews.models import Category, Comment, Genre, Title, Review, User
from reviews.models import USER_EMAIL_MAX_LENGTH, USER_USERNAME_MAX_LENGTH

USER_FORBIDDEN_NAMES = ('me',)


class CategoryField(SlugRelatedField):

    def to_representation(self, value):
        return CategorySerializer(value).data


class CategorySerializer(ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class CommentSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class GenreSerializer(ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        ordering = ('name',)


class GenreField(SlugRelatedField):

    def to_representation(self, value):
        return GenreSerializer(value).data


class TitleSerializer(ModelSerializer):
    category = CategoryField(
        queryset=Category.objects.all(),
        required=False,
        slug_field='slug')
    genre = GenreField(
        many=True,
        queryset=Genre.objects.all(),
        required=False,
        slug_field='slug')
    rating = IntegerField(
        required=False)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        author = self.context['request'].user
        if Review.objects.filter(title_id=title_id, author=author).exists():
            raise ValidationError(
                'Вы уже оставляли обзор на данное произведение')
        return data


class UserSignUpSerializer(Serializer):
    username = RegexField(r'^[\w.@+-]+', max_length=USER_USERNAME_MAX_LENGTH)
    email = EmailField(max_length=USER_EMAIL_MAX_LENGTH)

    def validate_username(self, value):
        if value not in USER_FORBIDDEN_NAMES:
            return value
        raise ValidationError(f"Имя пользователя '{value}' запрещено.")
    
    def validate(self, data):
        err = ''
        if (User.objects.filter(email=data['email']).exists() and
                User.objects.get(
                    email=data['email']).username != data['username']):
            err = f"Данный адрес электронной почты уже занят"
        elif (User.objects.filter(username=data['username']).exists() and
                User.objects.get(
                    username=data['username']).email != data['email']):
            err = f"Данное имя пользователя уже занято"
        if err:
            raise ValidationError()
        return data


class UsersSerializerAdmin(ModelSerializer):
    lookup_field = 'username'

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
