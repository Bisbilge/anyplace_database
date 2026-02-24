from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Doğru kullanım budur
    path('', include('places.urls')),
]