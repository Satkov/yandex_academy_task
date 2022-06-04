import math

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Product
from .utils import get_request, is_valid_uuid4


class ChildrenSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'id', 'parent_id', 'date', 'price', 'type')

    def get_parent_id(self, obj):
        return obj.parents.id


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    parent_id = serializers.UUIDField(write_only=True, required=False)
    parent_id = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'type', 'parent_id', 'date', 'price', 'children')

    def validate(self, data):
        print(data)
        request_data = get_request(self.context).data

        # Проверка на наличие поля 'id' в request
        if 'id' not in request_data:
            raise serializers.ValidationError({
                'errors': 'id is required'
            })

        # Проверка уникальности id
        if Product.objects.filter(id=request_data.get('id')).exists():
            raise serializers.ValidationError({
                'errors': 'Product with such id is already exists'
            })

        data['id'] = request_data.get('id')

        if 'parent_id' in request_data:
            parent_id = request_data.get('parent_id')

            # Проверка наличия объекта Product с предоставленным id в БД
            if not Product.objects.filter(id=parent_id).exists():
                raise serializers.ValidationError({
                    'errors': "Product with such parent_id doesn't exists"
                })
            data['parent_id'] = parent_id

        if 'price' in request_data:
            price = request_data.get('price')
            # Проверка типа поля id
            try:
                int(price)
            except ValueError:
                raise serializers.ValidationError({
                    'errors': "Price must be int"
                })
            data['price'] = price

        return data

    def create(self, validated_data):
        product = Product.objects.create(
            id=validated_data.get('id'),
            name=validated_data.get('name'),
            type=validated_data.get('type'),
        )
        if 'price' in validated_data:
            product.price = validated_data.get('price')

        if 'parent_id' in validated_data:
            parent = get_object_or_404(Product, id=validated_data.get('parent_id'))
            product.parents = parent
        product.save()
        return product

    def get_price(self, obj):
        if obj.type == 'OFFER':
            return obj.price

        children = obj.children.all()
        if not children:
            return 0

        price = 0
        for child in children:
            price += child.price
        return math.floor(price / len(children))

    def get_parent_id(self, obj):
        parent = obj.parents
        if parent:
            return obj.parents.id
        return parent

    def get_children(self, obj):
        childrens = obj.children.all()
        serializer = ChildrenSerializer(childrens, many=True)
        return serializer.data
