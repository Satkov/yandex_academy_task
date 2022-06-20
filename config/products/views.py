from datetime import timedelta

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Product, ProductHistory
from .serializers import (ProductCreateUpdateDeleteSerializer,
                          ProductRetrieveSerializer, SalesProductSerializer)
from .utils import (get_product_history_date_range_queryset,
                    get_product_objs_by_ids_from_product_history,
                    parse_date_from_request, put_product_history_data_into_dict,
                    split_categories_from_offers)


class ProductViewSet(mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ProductRetrieveSerializer
        return ProductCreateUpdateDeleteSerializer

    def create(self, request, *args, **kwargs):
        """
        Категории и товары создаются отедльно,
        чтобы категории можно было использовать в качестве
        родителя для товаров из того же запроса
        """
        categories, offers = split_categories_from_offers(request.data)
        if categories:
            serializer = self.get_serializer(data=categories, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        if offers:
            serializer = self.get_serializer(data=offers, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='statistic')
    def statistic(self, request, pk=None):
        start = parse_date_from_request(request, 'dateStart')
        end = parse_date_from_request(request, 'dateEnd')
        queryset = get_product_history_date_range_queryset(pk, start, end)
        history = put_product_history_data_into_dict(queryset)
        serializer = SalesProductSerializer(data=history, many=True)
        serializer.is_valid(raise_exception=True)
        data = {'items': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='sales')
    def sales(self, request, pk=None):
        end = parse_date_from_request(request, 'date', raise_exceptions=True)
        start = end - timedelta(days=1)
        queryset = ProductHistory.objects.filter(date__range=[start, end],
                                                 price_changed=True,
                                                 type='OFFER')
        products = get_product_objs_by_ids_from_product_history(queryset)
        serializer = SalesProductSerializer(data=products, many=True)
        serializer.is_valid(raise_exception=True)
        data = {'items': serializer.data}
        return Response(data, status=status.HTTP_200_OK)
