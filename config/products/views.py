from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from .serializers import ProductSerializer
from .models import Product


class ProductViewSet(mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()