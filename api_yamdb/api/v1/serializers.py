from rest_framework.serializers import ModelSerializer, SlugRelatedField

from reviews.models import Category, Genre, Title, User


class CategoryField(SlugRelatedField):

    def to_representation(self, value):
        return CategorySerializer(value).data


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreField(SlugRelatedField):

    def to_representation(self, value):
        return GenreSerializer(value).data


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        ordering = ('name',)


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

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


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
