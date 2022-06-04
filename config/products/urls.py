from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProductViewSet

router = DefaultRouter()
router.register(r'boards', ProductViewSet)


urlpatterns = format_suffix_patterns([
    path('nodes/<uuid:pk>/', ProductViewSet.as_view({'get': 'retrieve'}), name='product-retrieve'),
    path('imports/', ProductViewSet.as_view({'post': 'create'}), name='product-create'),
])
