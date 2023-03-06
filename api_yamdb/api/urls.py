from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .v1.views import (
    auth_token,
    AuthSignupViewSet,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UsersViewSet)


def router_register_func(router, patterns):
    for data in patterns:
        router.register(data[0], data[1], basename=data[2])


v1_router = DefaultRouter()
v1_router_patterns = [
    ('auth/signup', AuthSignupViewSet, 'signup'),
    ('categories', CategoryViewSet, 'categories'),
    ('genres', GenreViewSet, 'genres'),
    ('titles', TitleViewSet, 'titles'),
    (r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, 'reviews'),
    (r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
     CommentViewSet, 'comments'),
    ('users', UsersViewSet, 'users')]

router_register_func(router=v1_router, patterns=v1_router_patterns)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/token/', auth_token, name='token')]