import re
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from simple_history.models import HistoricalRecords

class Category(models.Model):
    """
    Projeyi indiren kişinin kendi mekan türlerini belirleyebilmesi için kategori modeli.
    Örn: 'Vegan Restoran', 'Antikacı', 'İkinci El Kıyafet' vb.
    """
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="İkon (Opsiyonel)")
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=255, verbose_name="Mekan Adı") 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='places', verbose_name="Kategori")
    
    latitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16, 
        null=True, 
        blank=True, 
        verbose_name="Enlem (Latitude)"
    )
    longitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16, 
        null=True, 
        blank=True, 
        verbose_name="Boylam (Longitude)"
    )
    
    maps_url = models.URLField(
        max_length=500, 
        null=True, 
        blank=True, 
        verbose_name="Google Maps Linki"
    )
    
    description = models.TextField(blank=True, verbose_name="Açıklama/Notlar")
    
    # Yönetim alanları
    is_approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Eklenme Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    # Geçmiş kayıtlarını tutacak olan nesne
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # 1. Uzun Google Maps Linkinden Koordinat Ayıklama (Offline/Statik)
        if self.maps_url and (not self.latitude or not self.longitude):
            pattern_std = r"([-+]?\d{1,2}\.\d+),\s*([-+]?\d{1,3}\.\d+)"
            pattern_long = r"!3d([-+]?\d{1,2}\.\d+)!4d([-+]?\d{1,3}\.\d+)"

            match = re.search(pattern_std, self.maps_url) or re.search(pattern_long, self.maps_url)

            if match:
                self.latitude = Decimal(match.group(1))
                self.longitude = Decimal(match.group(2))

        # 2. Hassas Yuvarlama (6 Hane Hassasiyeti)
        if self.latitude is not None:
            self.latitude = Decimal(str(self.latitude)).quantize(
                Decimal('0.000001'), 
                rounding=ROUND_HALF_UP
            )
        if self.longitude is not None:
            self.longitude = Decimal(str(self.longitude)).quantize(
                Decimal('0.000001'), 
                rounding=ROUND_HALF_UP
            )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mekan"
        verbose_name_plural = "Mekanlar"
        ordering = ['-created_at']


class PlaceReport(models.Model):
    # Şikayet seçenekleri her mekana uyacak şekilde genelleştirildi
    ISSUE_CHOICES = [
        ('kapali_yok', 'Mekan Kapalı / Artık Yok'),
        ('bilgi_hatali', 'Mekan Bilgileri Hatalı / Eksik'),
        ('konum_yanlis', 'Haritadaki Konum Yanlış'),
        ('diger', 'Diğer'),
    ]

    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reports', verbose_name="İlgili Mekan")
    reason = models.CharField(max_length=50, choices=ISSUE_CHOICES, verbose_name="Bildirim Nedeni")
    description = models.TextField(blank=True, null=True, verbose_name="Ek Açıklama (İsteğe Bağlı)")
    
    is_resolved = models.BooleanField(default=False, verbose_name="Çözüldü mü?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Bildirim Tarihi")

    class Meta:
        verbose_name = "Mekan Bildirimi"
        verbose_name_plural = "Mekan Bildirimleri"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_reason_display()}] - {self.place.name}"