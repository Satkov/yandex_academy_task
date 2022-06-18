from django.contrib import admin

from .models import Product, ProductHistory


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date', 'type', 'price')


class ProductHistoryAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'date', 'parentId', 'type', 'price', 'price_changed')


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductHistory, ProductHistoryAdmin)

