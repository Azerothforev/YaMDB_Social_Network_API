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


titles_patterns = [
    ('titles', TitleViewSet, 'titles'),
    (r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, 'reviews'),
    (r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
     CommentViewSet, 'comments')]
router_patterns = [
    ('categories', CategoryViewSet, 'categories'),
    ('genres', GenreViewSet, 'genres'),
    ('users', UsersViewSet, 'users')]
for endpoint in (titles_patterns,):
    for pattern in endpoint:
        router_patterns.append(pattern)

router = DefaultRouter()
router_register_func(router=router, patterns=router_patterns)

v1_urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', auth_signup, name='signup'),
    path('auth/token/', auth_token, name='token')]
