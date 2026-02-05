# attendance_system/urls.py - CORRECT VERSION
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('attendance/', include('attendance.urls')),
    path('api/', include('api.urls')),
]