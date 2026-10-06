"""
URL Configuration for PharmaCare.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Storefront & Catalog
    path('', include('apps.products.urls', namespace='products')),
    
    # User Accounts & Profiles
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    
    # Cart & Checkout
    path('cart/', include('apps.cart.urls', namespace='cart')),
    
    # Orders & Tracking
    path('orders/', include('apps.orders.urls', namespace='orders')),
    
    # Prescriptions
    path('prescriptions/', include('apps.prescriptions.urls', namespace='prescriptions')),
    
    # Deliveries
    path('deliveries/', include('apps.deliveries.urls', namespace='deliveries')),
    
    # Reviews
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    
    # Notifications
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    
    # Role-Based Dashboards
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # Inventory
    path('inventory/', include('apps.inventory.urls', namespace='inventory')),
    
    # REST API v1
    path('api/v1/', include('api.urls', namespace='api_v1')),
    
    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'apps.common.views.handler404'
handler403 = 'apps.common.views.handler403'
handler500 = 'apps.common.views.handler500'
