from django.contrib import admin
from django.db.models import Max
from django.utils.html import format_html

from main.models import Product, Category, Order
from users.models import User

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'weight', 'measure', 'price', 'category',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'is_hidden',)


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    readonly_fields = ['order_datetime', 'delivery_address', 'order_amount', 'payment_method', 'view_order_link']

    def view_order_link(self, obj):
        return format_html('<a href="{}">View Order</a>', obj.get_admin_url())

    view_order_link.short_description = 'Order'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'total_amount', 'last_order_info',)
    inlines = [OrderInline]

    def get_last_order_info(self, obj):
        last_order = obj.order_set.annotate(max_order_datetime=Max('order_datetime')).order_by(
            '-max_order_datetime').first()
        if last_order:
            return f'{last_order.order_datetime} - {last_order.order_amount} руб.'
        return '-'

    get_last_order_info.short_description = 'Last Order'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('order_set__products')

    def last_order_info(self, obj):
        return self.get_last_order_info(obj)

    last_order_info.admin_order_field = 'order_set__order_datetime'
