from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.billing_list, name='billing_list'),
    path('<int:pk>/', views.billing_detail, name='billing_detail'),
]