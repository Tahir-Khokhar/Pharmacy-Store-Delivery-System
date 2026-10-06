from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list_view, name='list'),
    path('adjust/', views.stock_adjust_view, name='adjust'),
    path('batch/add/', views.batch_create_view, name='batch_add'),
]
