# 🌍 AnyPlace Database Altyapısı

> İstediğiniz her türlü mekanın harita tabanlı veritabanını oluşturun.  
> Vegan restoranlar, ücretsiz tuvaletler, bisiklet durakları… Karar sizin!

---

## 🚀 Hızlı Başlangıç

Tek bir komutla kurulum sihirbazını başlatın:

```bash
git clone https://github.com/Bisbilge/anyplace_database.git && cd anyplace_database && python setup_wizard.py
```

Komut şunları otomatik olarak yapar:
- Sanal ortamı (venv) oluşturur
- Kurulum sihirbazı penceresini açar
- Sizi adım adım yönlendirir

> 💡 **Python 3.8+** yüklü olması yeterli. Başka bir şey kurmanıza gerek yok.

---

## 🧙 Kurulum Sihirbazı — Adım Adım

Sihirbaz açıldığında 7 adımdan geçeceksiniz. Her adım için ne yapmanız gerektiğini aşağıda açıkladık.

---

### 1️⃣ GitHub Yapılandırması

Projenizin kodları GitHub'da saklanacak.

**Yapmanız gerekenler:**
1. [github.com/new](https://github.com/new) adresine gidin
2. **"Private"** seçeneğiyle yeni bir repo oluşturun
3. Repo adını not edin (örn: `benim-cafe-haritam`)
4. Sihirbaza GitHub kullanıcı adınızı, repo adınızı ve Django klasör adını girin

> 🔒 GitHub hesabınız yoksa [buradan](https://github.com/signup) ücretsiz açabilirsiniz.

---

### 2️⃣ Veritabanı — Neon.tech

Mekan verileriniz ücretsiz bir Postgres veritabanında tutulacak.

**Yapmanız gerekenler:**
1. [console.neon.tech](https://console.neon.tech/) adresine gidin (ücretsiz kayıt)
2. Yeni bir proje oluşturun
3. **Connection Details** bölümünden **Connection String**'i kopyalayın
   - Şuna benzer bir URL: `postgresql://user:sifre@host/dbname`
4. Sihirbaza yapıştırın

---

### 3️⃣ Güvenlik — Google reCAPTCHA

Sitenizi botlardan korumak için reCAPTCHA ekliyoruz.

**Yapmanız gerekenler:**
1. [Google reCAPTCHA Yönetim Paneli](https://www.google.com/recaptcha/admin/create)'ni açın
2. **reCAPTCHA v2** seçin
3. Domain olarak `<repo-adınız>.vercel.app` ekleyin
4. **Site Key** ve **Secret Key**'i kopyalayıp sihirbaza yapıştırın

---

### 4️⃣ Yapılandırma (Otomatik ⚙️)

Bu adımda sihirbaz her şeyi sizin için yapar:

- `vercel.json` dosyasını oluşturur
- Güvenli bir `SECRET_KEY` üretir
- `.env` dosyasını hazırlar
- `pip install` ile gerekli kütüphaneleri kurar
- Neon veritabanında tabloları oluşturur (`migrate`)

Sadece bekleyin, log ekranında ilerlemeyi canlı görebilirsiniz. ✅

---

### 5️⃣ Admin Hesabı 👤

Site yönetim panelinize giriş için bir admin hesabı oluşturun.

Sihirbaz formu doldurmanızı isteyecek:

| Alan | Açıklama |
|------|----------|
| Kullanıcı Adı | Yönetici giriş adı (örn: `admin`) |
| E-posta | Bildirimler için |
| Şifre | En az 8 karakter |

> 🔐 Şifrenizi güvenli bir yere kaydedin! Yönetim paneline `siteniz.vercel.app/admin` adresinden gireceksiniz.

---

### 6️⃣ GitHub'a Yükleme (Otomatik 🚀)

Sihirbaz projenizi otomatik olarak GitHub'a yükler:

```
git init → git add . → git commit → git push
```

Yine sadece bekleyin, log ekranından canlı takip edebilirsiniz.

---

### 7️⃣ Vercel Deploy 🎉

Son adımda Vercel deploy sayfası otomatik açılır.

**Yapmanız gerekenler:**
1. GitHub reponuzu seçin
2. **Environment Variables** bölümüne sihirbazın son ekranındaki anahtarları kopyalayın  
   (Her birinin yanında 📋 kopyala butonu var)
3. **Deploy** butonuna tıklayın

Birkaç dakika sonra siteniz `https://<repo-adınız>.vercel.app` adresinde yayında! 🌐

---

## 🛠️ Gereksinimler

| Gereksinim | Detay |
|------------|-------|
| Python | 3.8 veya üzeri |
| Git | Yüklü olmalı ([git-scm.com](https://git-scm.com)) |
| GitHub Hesabı | Ücretsiz |
| Neon Hesabı | Ücretsiz |
| Google Hesabı | reCAPTCHA için |
| Vercel Hesabı | Ücretsiz ([vercel.com](https://vercel.com)) |

---

## ❓ Sık Sorulan Sorular

**Kod bilmem gerekiyor mu?**  
Hayır! Kurulum sihirbazı her şeyi sizin için yapıyor. Sadece bilgileri formlara girin.

**Veriler nerede saklanıyor?**  
Tüm mekan verileri Neon.tech'deki ücretsiz Postgres veritabanınızda saklanır. Tamamen size aittir.

**Kurulum sırasında hata alırsam?**  
Her adımda hata mesajı ekranda görünür. Sorununuzu [Issues](https://github.com/Bisbilge/anyplace_database/issues) sayfasından bildirebilirsiniz.

**Ücretsiz mi?**  
Evet! GitHub, Neon ve Vercel'in ücretsiz katmanları bu proje için yeterli.

---

## 📬 İletişim & Destek

Bir sorunuz mu var? [GitHub Issues](https://github.com/Bisbilge/anyplace_database/issues) üzerinden ulaşabilirsiniz.

---

<p align="center">
  <sub>❤️ AnyPlace — Herkes için, her mekan için.</sub>
</p>
