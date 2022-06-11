import math
from queue import Queue

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Product
from .utils import ChangeParentDate


class ProductCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    parentId = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Product.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = ('id', 'name', 'date', 'type', 'parentId', 'price')

    def validate(self, data):
        if not data.get('type') == 'OFFER' and 'price' in data:
            raise serializers.ValidationError({
                'code': 400,
                'message': "Category can't have a price"
            })

        if 'parentId' in data and data.get('parentId'):
            parent = get_object_or_404(Product, id=data.get('parentId').id)
            if parent.type != 'CATEGORY':
                raise serializers.ValidationError({
                    'code': 400,
                    'message': "OFFER can't be a parent"
                })

        return data

    def create(self, validated_data):
        if not Product.objects.filter(id=validated_data.get('id')).exists():
            product = Product(
                id=validated_data.get('id'),
                name=validated_data.get('name'),
                type=validated_data.get('type'),
                date=validated_data.get('date'),
                parentId=validated_data.get('parentId'),
                price=validated_data.get('price')
            )

            if validated_data.get('parentId'):
                ChangeParentDate(validated_data['parentId'], validated_data.get('date'))

            product.save()
            return product
        product = get_object_or_404(Product, id=validated_data.get('id'))
        return self.update(product, validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.type = validated_data.get('type')
        instance.date = validated_data.get('date')

        if 'price' not in validated_data:
            if validated_data.get('type') == 'OFFER':
                instance.price = 0
            else:
                instance.price = None
        else:
            instance.price = validated_data.get('price')

        if not validated_data.get('parentId'):
            instance.parentId = None
        else:
            instance.parentId = validated_data.get('parentId')
            ChangeParentDate(validated_data['parentId'], validated_data.get('date'))
        instance.save()
        return instance


class ProductRetrieveSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('name', 'id', 'parentId', 'date', 'price', 'type', 'children')

    def get_children(self, obj):
        children = obj.children.all()
        if not children:
            return None
        serializer = ProductRetrieveSerializer(children, many=True)
        return serializer.data

    def get_price(self, obj):
        """
        :param obj: Product obj
        :return: int

        Если тип объекта категория, -
        считает сумму стуимости всех дочерних элементов.
        """
        if obj.type == 'OFFER':
            return obj.price

        q = Queue()
        for child in obj.children.all():
            q.put(child)

        price = 0
        counter = 0
        while not q.empty():
            child = q.get()
            if child.type == 'CATEGORY':
                for c in child.children.all():
                    q.put(c)
            else:
                counter += 1
                price += child.price

        if counter == 0:
            return 0

        return math.floor(price / counter)

    def get_date(self, obj):
        return obj.date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


class ProductHistorySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')
    parentId = serializers.UUIDField(required=False, allow_null=True)
    price = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.CharField()
