from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    category = CharFilter(
        field_name='category__slug',
        lookup_expr='contains')
    genre = CharFilter(
        field_name='genre__slug',
        lookup_expr='contains')
    name = CharFilter(
        field_name='name',
        lookup_expr='contains')

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category')
