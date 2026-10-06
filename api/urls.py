from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .views import (
    RegisterAPIView,
    CurrentUserAPIView,
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    OrderViewSet,
    PrescriptionViewSet,
    DeliveryViewSet,
    ReviewViewSet,
    NotificationViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='api-category')
router.register(r'products', ProductViewSet, basename='api-product')
router.register(r'cart', CartViewSet, basename='api-cart')
router.register(r'orders', OrderViewSet, basename='api-order')
router.register(r'prescriptions', PrescriptionViewSet, basename='api-prescription')
router.register(r'deliveries', DeliveryViewSet, basename='api-delivery')
router.register(r'reviews', ReviewViewSet, basename='api-review')
router.register(r'notifications', NotificationViewSet, basename='api-notification')

app_name = 'api_v1'

urlpatterns = [
    # Router endpoints
    path('', include(router.urls)),

    # Authentication & JWT
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='api-me'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # OpenAPI 3 Schema & Swagger / ReDoc Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
