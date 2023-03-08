from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
    SlugRelatedField,
    ValidationError)

from reviews.models import Category, Comment, Genre, Title, Review, User


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


class UserSignUpSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')


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
