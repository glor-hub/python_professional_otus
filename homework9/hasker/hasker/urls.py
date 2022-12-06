from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from hasker.settings import DEBUG

urlpatterns = [
    path('hasker/', include('main.urls', namespace='main')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('admin/', admin.site.urls),
]

if DEBUG:
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),
if DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
