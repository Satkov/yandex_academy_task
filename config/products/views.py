from datetime import timedelta

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Product, ProductHistory
from .serializers import (ProductCreateUpdateDeleteSerializer,
                          ProductHistorySerializer, ProductRetrieveSerializer)
from .utils import (GetProductHistoryDateRangeQueryset, ParseDateFromRequest,
                    PutProductHistoryDataIntoDict, SplitCategoriesFromOffers)


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
        CATEGORIES, OFFERS = SplitCategoriesFromOffers(request.data)
        if CATEGORIES:
            serializer = self.get_serializer(data=CATEGORIES, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        if OFFERS:
            serializer = self.get_serializer(data=OFFERS, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='statistic')
    def statistic(self, request, pk=None):
        start = ParseDateFromRequest(request, 'dateStart')
        end = ParseDateFromRequest(request, 'dateEnd')
        queryset = GetProductHistoryDateRangeQueryset(pk, start, end)
        history = PutProductHistoryDataIntoDict(queryset)
        serializer = ProductHistorySerializer(data=history, many=True)
        serializer.is_valid(raise_exception=True)
        data = {'items': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='sales')
    def sales(self, request, pk=None):
        end = ParseDateFromRequest(request, 'date')
        start = end - timedelta(days=1)
        queryset = ProductHistory.objects.filter(date__range=[start, end],
                                                 price_changed=True)
        history = PutProductHistoryDataIntoDict(queryset)
        serializer = ProductHistorySerializer(data=history, many=True)
        serializer.is_valid(raise_exception=True)
        data = {'items': serializer.data}
        return Response(data, status=status.HTTP_200_OK)
