import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Place, PlaceReport 
from .forms import PlaceForm, PlaceReportForm 

# Hataları loglamak için
logger = logging.getLogger(__name__)

def index(request):
    """Ana sayfa."""
    return render(request, 'index.html')

def places_data(request):
    """Harita için sadece ONAYLANMIŞ ve KOORDİNATI OLAN mekanları JSON olarak döndürür."""
    # Veritabanına daha az sorgu atmak için select_related ile kategorileri de çekiyoruz
    places = Place.objects.filter(is_approved=True).select_related('category')
    data = []

    for p in places:
        if p.latitude is not None and p.longitude is not None:
            data.append({
                'id': p.id, 
                'name': p.name,
                'lat': float(p.latitude),
                'lng': float(p.longitude),
                # Jenerik alanlarımızı JSON'a ekliyoruz
                'category_name': p.category.name if p.category else "Diğer",
                'category_icon': p.category.icon if p.category and p.category.icon else "",
                'desc': p.description
            })

    return JsonResponse(data, safe=False)

def add_place(request):
    """Yeni mekan ekleme sayfası. (Eski adıyla report_toilet)"""
    if request.method == 'POST':
        # Honeypot ve Spam Filtresi (Açık kaynak repo için genel geçer kelimeler)
        honeypot = request.POST.get('website_url')
        name_input = request.POST.get('name', '').upper()
        spam_keywords = ['SPAM', 'TEST', 'REKLAM', 'CASINO']

        if honeypot or any(word in name_input for word in spam_keywords):
            return render(request, 'success.html')

        form = PlaceForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'success.html')
    else:
        form = PlaceForm()

    # Template ismini jenerik olması için 'add_place.html' olarak düşündüm
    return render(request, 'add_place.html', {'form': form}) 


def report_place_issue(request):
    """Haritadaki mevcut bir mekan için hata/şikayet bildirme sayfası."""
    place_id = request.GET.get('id')
    
    if not place_id or not place_id.isdigit():
        return redirect('index')

    target_place = get_object_or_404(Place, id=place_id)

    if request.method == 'POST':
        if request.POST.get('website_url'):
            return render(request, 'success.html', {'mail_sent': True})

        form = PlaceReportForm(request.POST)
        
        if form.is_valid():
            issue = form.save(commit=False)
            issue.place = target_place 
            issue.save() 
            
            return render(request, 'success.html', {'mail_sent': True})
    else:
        form = PlaceReportForm()

    return render(request, 'report_issue.html', {
        'form': form,
        'place': target_place
    })