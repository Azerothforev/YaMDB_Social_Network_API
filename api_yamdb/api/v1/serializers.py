from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    IntegerField,
    Serializer,
    SlugRelatedField,
    RegexField,
    ValidationError)

from reviews.models import Category, Comment, Genre, Title, Review, User

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
        title = get_object_or_404(
            Title,
            pk=self.context['view'].kwargs.get('title_id'))
        author = self.context['request'].user
        if Review.objects.filter(title_id=title, author=author).exists():
            raise ValidationError(
                'Вы уже оставляли обзор на данное произведение')
        return data


class UserSignUpSerializer(Serializer):
    username = RegexField(r'^[\w.@+-]+', max_length=150)
    email = EmailField(max_length=254)

    def validate_username(self, value):
        if value not in USER_FORBIDDEN_NAMES:
            return value
        raise ValidationError(f"Имя пользователя '{value}' запрещено.")


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
