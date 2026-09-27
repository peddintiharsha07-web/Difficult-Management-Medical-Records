from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('users.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('emergency/', include('emergency.urls')),
    path('administration/', include('administration.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
