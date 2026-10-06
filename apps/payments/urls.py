from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list_view, name='list'),
    path('<int:pk>/', views.payment_detail_view, name='detail'),
    path('<int:pk>/mark-paid/', views.payment_mark_paid_action, name='mark_paid'),
]
