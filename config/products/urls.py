from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProductViewSet

urlpatterns = format_suffix_patterns([
    path('sales', ProductViewSet.as_view({'get': 'sales'}), name='product-sales'),
    path('node/<uuid:pk>/statistic', ProductViewSet.as_view({'get': 'statistic'}), name='product-history'),
    path('delete/<uuid:pk>', ProductViewSet.as_view({'delete': 'destroy'}), name='product-destroy'),
    path('nodes/<uuid:pk>', ProductViewSet.as_view({'get': 'retrieve'}), name='product-retrieve'),
    path('imports', ProductViewSet.as_view({'post': 'create'}), name='product-create'),
])
