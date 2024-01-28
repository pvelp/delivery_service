from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView

from main.serializers import ProductSerializer
from main.filters import ProductFilter
from main.models import Product


class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    filterset_fields = ['category']
    #  TODO:Пагинация

    def get_queryset(self):
        category_ids = self.request.query_params.getlist('categories', [])
        if category_ids:
            return Product.objects.filter(category_id__in=category_ids)
        return Product.objects.all()


class ProductRetrieveAPIView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
