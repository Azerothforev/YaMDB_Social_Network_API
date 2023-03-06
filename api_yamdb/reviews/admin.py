from django.contrib.admin import site

from .models import Category, Genre, Title, User

site.register(User)
site.register(Category)
site.register(Genre)
site.register(Title)
