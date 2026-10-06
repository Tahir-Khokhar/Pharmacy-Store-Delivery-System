from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.role_dashboard_router, name='router'),
    path('admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('pharmacist/', views.pharmacist_dashboard_view, name='pharmacist'),
    path('customer/', views.customer_dashboard_view, name='customer'),
]
