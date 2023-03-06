from django.contrib.admin import site

from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


site.register(Category)
site.register(Comment)
site.register(Genre)
site.register(GenreTitle)
site.register(Review)
site.register(Title)
site.register(User)
