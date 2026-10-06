from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list_view, name='order_list'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation_view, name='confirmation'),
    path('detail/<str:order_number>/', views.order_detail_view, name='detail'),
    path('invoice/<str:order_number>/', views.order_invoice_view, name='invoice'),
    path('cancel/<str:order_number>/', views.cancel_order_view, name='cancel'),
    path('update-status/<str:order_number>/', views.update_order_status_view, name='update_status'),
]
