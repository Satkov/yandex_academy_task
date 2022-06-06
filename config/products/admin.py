from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Product


class ProductAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'name', 'date', 'type', 'price')


admin.site.register(Product, ProductAdmin)
