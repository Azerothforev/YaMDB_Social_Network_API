from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField,
    EmailField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    Model,
    SET_NULL,
    SlugField,
    TextField)


class Category(Model):
    """Модель категорий"""
    name = CharField('Название категории', max_length=256)
    slug = SlugField('Слаг категории', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(Model):
    """Модель жанров"""
    name = CharField('Название жанра', max_length=256)
    slug = SlugField('Слаг жанра', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанры'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(Model):
    category = ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name="titles",
        verbose_name="Категория_произведения",
    )
    description = CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Описание произведения",
    )
    genre = ManyToManyField(
        Genre,
        blank=True,
        related_name="titless",
        verbose_name="Жанр_произведения",
    )
    name = CharField(
        max_length=100,
        verbose_name="Название произведения",
    )
    year = IntegerField('Год издания')

    class Meta:
        verbose_name = 'Произведения'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
        ('superuser', 'superuser')]
    bio = TextField(
        max_length=256,
        blank=True,
        null=True,
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
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Статус на сайте')

    class Meta:
        verbose_name = 'пользователь',
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
