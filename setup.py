import os, secrets, time, subprocess, webbrowser, json, sys, shutil

def clear_screen(): os.system('clear' if os.name != 'nt' else 'cls')

def print_header(step_num, title):
    clear_screen()
    print("=" * 80)
    print(f" 🛠️  ANYPLACE ULTIMATE KURULUM | ADIM {step_num} / 6")
    print("=" * 80)
    print(f"\n>>> {title.upper()} <<<\n")

def run_command(command, description, interactive=False):
    """Logları canlı görmek için capture_output kaldırıldı."""
    print(f"\n[İŞLEM] {description}...")
    try:
        if interactive:
            return subprocess.call(command, shell=True) == 0
        else:
            # stdout ve stderr None bırakılarak logların terminale akması sağlandı
            subprocess.run(command, shell=True, check=True)
            return True
    except Exception as e:
        print(f"⚠️ Hata oluştu: {e}")
        return False

def is_venv():
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def main():
    # --- ADIM 0: VENV YÖNETİMİ ---
    if not os.path.exists("venv"):
        print("📦 Sanal ortam (venv) oluşturuluyor...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    if not is_venv():
        python_exe = os.path.join("venv", "bin", "python")
        subprocess.run([python_exe] + sys.argv)
        print("\n✨ Kurulum bitti. Sanal ortam aktif kabuk açılıyor...")
        subprocess.run(["bash", "--rcfile", "venv/bin/activate"], check=False)
        sys.exit()

    try:
        # ADIM 1: GITHUB
        print_header(1, "GitHub Yapılandırması")
        print("1. Tarayıcıda GitHub açılıyor.")
        print("2. Lütfen 'Private' bir repo oluştur.")
        print("3. İşlemin bitince buraya dön.")
        time.sleep(2)
        webbrowser.open("https://github.com/new")
        input("\n✅ Repoyu oluşturduysan devam etmek için ENTER'a bas...")
        
        github_username = input("👉 GitHub Kullanıcı Adın: ").strip()
        repo_name = input("👉 Açtığın Repo Adı: ").strip().lower().replace(" ", "-")
        project_folder = input("👉 Django Klasör Adı (Örn: core): ").strip() or "core"
        
        base_domain = f"{repo_name}.vercel.app"
        repo_url = f"https://github.com/{github_username}/{repo_name}.git"

        # ADIM 2: NEON
        print_header(2, "Veritabanı (Neon.tech)")
        print("1. Neon dashboard açılıyor.")
        print("2. 'Connection String' kısmından DATABASE_URL'i kopyala.")
        time.sleep(1)
        webbrowser.open("https://console.neon.tech/")
        db_url = input("\n👉 Kopyaladığın DATABASE_URL'i yapıştır: ").strip()

        # ADIM 3: RECAPTCHA
        print_header(3, "Güvenlik (reCAPTCHA)")
        print(f"1. Kayıt sayfasına şu domaini ekle: {base_domain}")
        time.sleep(1)
        webbrowser.open("https://www.google.com/recaptcha/admin/create")
        recaptcha_public = input("\n👉 Site Key (Public): ").strip()
        recaptcha_private = input("👉 Secret Key (Private): ").strip()

        # ADIM 4: YAPILANDIRMA
        print_header(4, "Dosya Üretimi ve Migration")
        
        # vercel.json
        with open("vercel.json", "w") as f:
            json.dump({
                "version": 2,
                "builds": [{"src": f"{project_folder}/wsgi.py", "use": "@vercel/python"}],
                "routes": [{"src": "/(.*)", "dest": f"{project_folder}/wsgi.py"}]
            }, f, indent=2)

        # .env
        secret_key = secrets.token_urlsafe(50)
        env_content = (
            f'DJANGO_SECRET_KEY="{secret_key}"\n'
            f'DATABASE_URL="{db_url}"\n'
            f'DEBUG=True\n'
            f'ALLOWED_HOSTS="localhost,127.0.0.1,{base_domain},.vercel.app"\n'
            f'RECAPTCHA_PUBLIC_KEY="{recaptcha_public}"\n'
            f'RECAPTCHA_PRIVATE_KEY="{recaptcha_private}"\n'
        )
        with open(".env", "w") as f: f.write(env_content)
        
        os.environ["DATABASE_URL"] = db_url

        # Canlı logları göreceğin kısım
        run_command("pip install -r requirements.txt", "Kütüphaneler kuruluyor")
        run_command("python manage.py migrate", "Neon tabloları oluşturuluyor")
        
        print("\n🔑 Admin hesabı oluşturma ekranı geliyor...")
        run_command("python manage.py createsuperuser", "Superuser oluşturma", interactive=True)

        # ADIM 5: GITHUB PUSH
        print_header(5, "GitHub Aktarımı")
        if os.path.exists(".git"): shutil.rmtree(".git")
        
        git_cmds = [
            "git init",
            "git add .",
            'git commit -m "🚀 Production-ready setup"',
            "git branch -M main",
            f"git remote add origin {repo_url}",
            "git push -u origin main --force"
        ]
        for cmd in git_cmds: run_command(cmd, f"Git komutu: {cmd}")

        # ADIM 6: FİNAL
        print_header(6, "Kurulum Tamamlandı!")
        print(f"✅ Vercel'e eklenecek anahtarlar ekranda.")
        print("-" * 40)
        print(f"DATABASE_URL: {db_url}")
        print(f"DJANGO_SECRET_KEY: {secret_key}")
        print("-" * 40)
        
        time.sleep(2)
        webbrowser.open(f"https://vercel.com/new/import?s={repo_url}")
        
        print("\n✅ Seni sanal ortamda bırakıyorum. 'python manage.py runserver' ile başlayabilirsin.")
        subprocess.run(["bash", "--rcfile", "venv/bin/activate"], check=False)

    except KeyboardInterrupt:
        print("\n❌ İşlem iptal edildi.")

if __name__ == "__main__":
    main()