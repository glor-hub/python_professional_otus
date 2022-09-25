from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from hasker.settings import DEBUG

from hasker import views

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls),
]

if DEBUG:
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),
if DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

