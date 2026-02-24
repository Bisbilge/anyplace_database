from django.urls import path
from . import views

urlpatterns = [
    # Ana Harita Sayfası
    path('', views.index, name='index'),
    
    # Haritaya JSON veri sağlayan API rotası
    path('api/places/', views.places_data, name='places_data'),
    
    # Yeni bir mekan ekleme rotası
    path('add-place/', views.add_place, name='add_place'),
    
    # Mevcut bir mekan için şikayet/hata bildirme rotası
    path('report-issue/', views.report_place_issue, name='report_place_issue'),
]