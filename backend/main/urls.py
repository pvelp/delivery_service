from django.urls import path

from main.apps import MainConfig
from main.views import (
    ProductListAPIView, ProductRetrieveAPIView, AddToCart, RemoveFromCart,
    CartView, ApplyPromoCode, OrderCreateAPIView)

app_name = MainConfig.name

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='products'),
    path('products/<int:pk>/', ProductRetrieveAPIView.as_view(), name='product'),
    path('add-to-cart/', AddToCart.as_view(), name='add_to_cart'),
    path('remove-from-cart/', RemoveFromCart.as_view(), name='remove_from_cart'),
    path('cart/', CartView.as_view(), name='cart'),
    path('apply-promo-code/', ApplyPromoCode.as_view(), name='apply_promo_code'),
    path('order/', OrderCreateAPIView.as_view(), name='order')
]
