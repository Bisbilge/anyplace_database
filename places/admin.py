from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from simple_history.admin import SimpleHistoryAdmin

# Yeni jenerik modellerimizi içeri aktarıyoruz
from .models import Category, Place, PlaceReport 

# --- YENİ EKLENEN KATEGORİ ADMİNİ ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

# --- MEKAN ADMİNİ (Eski ToiletAdmin) ---
@admin.register(Place)
class PlaceAdmin(SimpleHistoryAdmin):
    # Kategori sütununu da admin paneline ekledik
    list_display = ('name', 'category', 'is_approved', 'show_maps_url', 'created_at')
    list_filter = ('is_approved', 'category')
    search_fields = ('name', 'description')
    
    history_list_display = ["is_approved"]
    
    def show_maps_url(self, obj):
        if obj.maps_url:
            return format_html('<a href="{0}" target="_blank" style="color: #2b7de9; font-weight: bold;">Haritada Aç</a>', obj.maps_url)
        return "Link Yok"
    show_maps_url.short_description = "Google Maps"

    actions = ['make_approved']
    
    @admin.action(description='Seçili mekanları onayla')
    def make_approved(self, request, queryset):
        queryset.update(is_approved=True)

    def get_readonly_fields(self, request, obj=None):
        # updated_at de eklendiği için onu da salt okunur yapıyoruz
        return ('created_at', 'updated_at')


# --- ŞİKAYET / RAPOR SİSTEMİ ADMİNİ (Eski ToiletReportAdmin) ---
@admin.register(PlaceReport)
class PlaceReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'reason', 'is_resolved', 'created_at')
    list_display_links = ('id', 'place') 
    
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('description', 'place__name')
    actions = ['mark_as_resolved']

    readonly_fields = ('related_place_link', 'created_at')

    def related_place_link(self, obj):
        if obj.id and obj.place:
            # Uygulama adı 'places' ve model 'place' olduğu için URL rotasını güncelledik
            url = reverse('admin:places_place_change', args=[obj.place.id])
            return format_html(
                '<a href="{}" style="background-color: #1E90FF; color: white; padding: 6px 12px; '
                'border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 13px;">'
                '🚀 {} Mekanını Düzenle'
                '</a>', 
                url, obj.place.name
            )
        return "-"
    
    related_place_link.short_description = 'Hızlı İşlem'

    @admin.action(description='Seçili bildirimleri "Çözüldü" olarak işaretle')
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)