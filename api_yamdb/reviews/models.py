from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    EmailField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    SET_NULL,
    SlugField,
    TextField,
    UniqueConstraint)


# Внимание! Не нужно создавать BaseTextModel для Comment и Review, так как
# в этом случае сервер не сможет запуститься с ошибкой:
# reviews.Comment.review: (models.E006) The field 'review' clashes with the
# field 'review' from model 'reviews.basetextmodel'.
class BaseGroupModel(Model):
    name = CharField(
        max_length=256,
        verbose_name='Название')
    slug = SlugField(
        max_length=50,
        unique=True,
        verbose_name='Краткий URL')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(BaseGroupModel):
    """Модель категорий"""

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'


class Genre(BaseGroupModel):
    """Модель жанров"""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(Model):
    """Модель произведений."""
    category = ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name='titles_cat',
        verbose_name='Категория')
    description = CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name='Описание')
    genre = ManyToManyField(
        Genre,
        blank=True,
        related_name='titles_gen',
        verbose_name='Жанр')
    name = CharField(
        max_length=100,
        verbose_name='Название')
    year = IntegerField('Год издания')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Модель пользователей."""
    ROLE_CHOICES = [
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
        ('superuser', 'superuser')]
    bio = TextField(
        blank=True,
        null=True,
        max_length=256,
        verbose_name='Биография')
    confirmation_code = CharField(
        blank=True,
        null=True,
        max_length=32,
        verbose_name='Код подтверждения')
    email = EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта')
    role = CharField(
        choices=ROLE_CHOICES,
        default='user',
        max_length=10,
        verbose_name='Статус на сайте')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class GenreTitle(Model):
    """Модель связи жанров и произведений."""
    genre = ForeignKey(
        Genre,
        on_delete=CASCADE,
        related_name='titles')
    title = ForeignKey(
        Title,
        on_delete=CASCADE,
        related_name='genres')

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class Review(Model):
    """Модель отзывов."""
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва')
    pub_date = DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')
    score = PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1, 'Минимальная оценка - 1'),
            MaxValueValidator(10, 'Максимальная оценка - 10')),
        verbose_name='Оценка произведения')
    text = TextField(
        max_length=256,
        verbose_name='Текст')
    title = ForeignKey(
        Title,
        on_delete=CASCADE,
        related_name='reviews',
        verbose_name='Произведение')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review')]
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(Model):
    """Модель комментариев."""
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='author',
        verbose_name='Автор комментария')
    pub_date = DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')
    review = ForeignKey(
        Review,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name='Комментируемый отзыв')
    text = TextField(
        max_length=256,
        verbose_name='Текст')

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
