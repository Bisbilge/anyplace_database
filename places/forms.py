from django import forms
from .models import Place, PlaceReport, Category
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

# 1. YENİ MEKAN EKLEME FORMU
class PlaceForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = Place
        # Tuvalete özel alanlar (is_free, price, code) çıkarıldı, category eklendi
        fields = ['name', 'category', 'maps_url', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mekan Adı (Örn: Kadıköy Sahaflar Çarşısı, Merkez Parkı)',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'maps_url': forms.URLInput(attrs={
                'placeholder': 'https://maps.google.com/...',
                'required': 'required',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mekan hakkında detaylar, nasıl gidilir veya önemli notlar...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        # Kategori seçimi için varsayılan boş etiketi ayarlıyoruz
        self.fields['category'].empty_label = "Lütfen bir kategori seçin"


# 2. MEVCUT MEKANI BİLDİRME/ŞİKAYET ETME FORMU
class PlaceReportForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = PlaceReport
        fields = ['reason', 'description']
        
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required',
                'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 2px solid #CED6E0; font-size: 16px;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                # Placeholder metni jenerik hale getirildi
                'placeholder': 'Lütfen durumu detaylıca açıklayın... (Örn: Bu mekan kapanmış, konumu haritada yanlış işaretlenmiş veya bilgileri eksik.)',
                'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 2px solid #CED6E0; font-size: 16px; margin-top: 10px;'
            }),
        }