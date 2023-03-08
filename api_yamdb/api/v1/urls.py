from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (
    auth_signup,
    auth_token,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UsersViewSet)


def router_register_func(router, patterns):
    for data in patterns:
        router.register(data[0], data[1], basename=data[2])


categories_patterns = [('categories', CategoryViewSet, 'categories')]
genres_patterns = [('genres', GenreViewSet, 'genres')]
titles_patterns = [('titles', TitleViewSet, 'titles'),
    (r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, 'reviews'),
    (r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
     CommentViewSet, 'comments')]
users_patterns = [('users', UsersViewSet, 'users')]
router = DefaultRouter()
router_patterns = []
for endpoint in (
        categories_patterns, genres_patterns, titles_patterns, users_patterns):
    for pattern in endpoint:
        router_patterns.append(pattern)

router_register_func(router=router, patterns=router_patterns)

v1_urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', auth_signup, name='signup'),
    path('auth/token/', auth_token, name='token')]
