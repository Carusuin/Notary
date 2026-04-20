from django.urls import path
from . import views
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

urlpatterns = [
    path('', views.index_deeds, name='index_deeds'),
    path('add/', views.add_deed, name='add_deed'),
    path('edit/<int:pk>/', views.edit_deed, name='edit_deed'), 
    path('delete/<int:pk>/', views.delete_deed, name='delete_deed'),
    path('export-pdf/<int:pk>/', views.export_deed_pdf, name='export_pdf'),
]