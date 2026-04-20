from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('add/', views.add_client, name='add_client'),
    path('edit/<int:pk>/', views.update_client, name='edit_client'),
    path('delete/<int:pk>/', views.delete_client, name='delete_client'),
]