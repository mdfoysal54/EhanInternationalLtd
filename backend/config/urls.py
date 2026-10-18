from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('workspace/', include('workspace.urls')),
    path('api/v1/', include('core.urls')),
    path('api/v1/operations/', include('operations.urls')),
    path('office/', include('office.urls')),
]
