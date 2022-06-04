from rest_framework import serializers

from .models import Product


class ChildrenSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'id', 'price', 'date', 'type', 'parent_id')

    def get_parent_id(self, obj):
        parent = obj.parents
        if parent:
            return obj.parents.id
        return parent


class ProductSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'date', 'type', 'parent_id', 'price', 'children')

    def get_parent_id(self, obj):
        parent = obj.parents
        if parent:
            return obj.parents.id
        return parent

    def get_children(self, obj):
        childrens = obj.children.all()
        serializer = ChildrenSerializer(childrens, many=True)
        return serializer.data
