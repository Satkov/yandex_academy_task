from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Product, ProductHistory


class ProductAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'name', 'date', 'type', 'price')


class ProductHistoryAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'date', 'parentId', 'type', 'price', 'date_updated')


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductHistory, ProductHistoryAdmin)
