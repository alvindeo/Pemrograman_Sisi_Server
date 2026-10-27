from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('silk/', include('silk.urls', namespace='silk')),
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
]