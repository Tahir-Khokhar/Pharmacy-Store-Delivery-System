from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('shop/', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('categories/', views.category_list_view, name='category_list'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('search/', views.search_view, name='search'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.wishlist_toggle_ajax, name='wishlist_toggle_ajax'),
]
