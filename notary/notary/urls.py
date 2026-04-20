from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    # Clients
    path('clients/', include('apps.clients.urls')), 
    path('clients/add/', include('apps.clients.urls')),
    # Deeds
    path('deeds/', include('apps.deeds.urls')),
    path('billing/', include('apps.finance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)