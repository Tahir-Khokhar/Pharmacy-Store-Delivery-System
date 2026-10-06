from django.urls import path
from . import views

app_name = 'deliveries'

urlpatterns = [
    path('', views.delivery_list_view, name='list'),
    path('<str:tracking_number>/', views.delivery_detail_view, name='detail'),
    path('<str:tracking_number>/update-status/', views.delivery_update_status, name='update_status'),
]
