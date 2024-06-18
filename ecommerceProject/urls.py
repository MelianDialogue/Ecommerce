from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from ml.urls import urlpatterns as ml_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user_app/', include('user_app.urls')),
    path('', include('store.urls')),
    path('ml/', include('ml.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += ml_urls