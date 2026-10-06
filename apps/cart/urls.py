from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/', views.add_to_cart_ajax, name='add_ajax'),
    path('update/', views.update_cart_item_ajax, name='update_ajax'),
    path('remove/', views.remove_cart_item_ajax, name='remove_ajax'),
    path('clear/', views.clear_cart_view, name='clear'),
]
