import django_filters
from main.models import Product


class ProductFilter(django_filters.rest_framework.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    description = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['title', 'price__gte', 'price__lte', 'description']
