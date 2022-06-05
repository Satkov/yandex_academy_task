import math
import uuid

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Product
from .utils import get_request, is_valid_uuid4


class ChildrenSerializer(serializers.ModelSerializer):
    parentId = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'id', 'parentId', 'date', 'price', 'type')

    def get_parent_id(self, obj):
        return obj.parents.id


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    parentId = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Product.objects.all(),
        required=False
    )

    class Meta:
        model = Product
        fields = ('id', 'name', 'type', 'parentId', 'date', 'price')

    def validate(self, data):
        print(data)
        if not data.get('type') == 'OFFER' and data.get('price') != 0:
            raise serializers.ValidationError({
                'errors': "Category can't have a price"
            })

        if 'parentId' in data:
            parent = get_object_or_404(Product, id=data.get('parentId').id)
            if parent.type != 'CATEGORY':
                raise serializers.ValidationError({
                    'errors': "OFFER can't be a parent"
                })

        return data

    def create(self, validated_data):
        print(validated_data)
        if not Product.objects.filter(id=validated_data.get('id')).exists():
            product = Product.objects.create(
                id=validated_data.get('id'),
                name=validated_data.get('name'),
                type=validated_data.get('type'),
            )
            if 'price' in validated_data:
                product.price = validated_data.get('price')

            if 'parentId' in validated_data:
                product.parentId = validated_data.get('parentId')
            product.save()
            return product

        else:
            product = get_object_or_404(Product, id=validated_data.get('id'))
            return self.update(product, validated_data)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        return instance

