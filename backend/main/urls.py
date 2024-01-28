from django.urls import path

from main.apps import MainConfig
from main.views import ProductListAPIView, ProductRetrieveAPIView

app_name = MainConfig.name

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='products'),
    path('products/<int:pk>/', ProductRetrieveAPIView.as_view(), name='product'),
]
