from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextField


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
