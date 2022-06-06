from rest_framework import mixins, status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializers import (ProductCreateUpdateDeleteSerializer,
                          ProductRetrieveSerializer,
                          ProductHistorySerializer)
from .models import Product
from .utils import SplitCategoryFromOffers


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
        CATEGORIES, OFFERS = SplitCategoryFromOffers(request.data['items'])
        if CATEGORIES:
            serializer = self.get_serializer(data=CATEGORIES, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        if OFFERS:
            serializer = self.get_serializer(data=OFFERS, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)


class ProductHistoryViewSet(mixins.RetrieveModelMixin,
                            GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductHistorySerializer
