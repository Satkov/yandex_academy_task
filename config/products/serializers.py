import math

from rest_framework import serializers

from .models import Product


class ChildrenSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'id', 'parent_id', 'date', 'price', 'type')

    def get_parent_id(self, obj):
        parent = obj.parents
        if parent:
            return obj.parents.id
        return parent


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    parent_id = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'type', 'parent_id', 'date', 'price', 'children')

    def get_price(self, obj):
        if obj.type == 'OFFER':
            return obj.price
        children = obj.children.all()
        price = 0
        for child in children:
            price += child.price
        return math.floor(price/len(children))

    def get_parent_id(self, obj):
        parent = obj.parents
        if parent:
            return obj.parents.id
        return parent

    def get_children(self, obj):
        childrens = obj.children.all()
        serializer = ChildrenSerializer(childrens, many=True)
        return serializer.data
