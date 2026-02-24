import os
import secrets
import time
import subprocess
import webbrowser
import json
import sys

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header(step_num, title):
    clear_screen()
    print("=" * 80)
    print(f" 🛠️  ANYPLACE ULTIMATE KURULUM | ADIM {step_num} / 6")
    print("=" * 80)
    print(f"\n>>> {title.upper()} <<<\n")

def is_venv():
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def run_command(command, description, interactive=False):
    print(f"\n[İŞLEM] {description}...")
    try:
        if interactive:
            return subprocess.call(command, shell=True) == 0
        else:
            subprocess.run(command, shell=True, check=True)
            return True
    except Exception as e:
        print(f"⚠️ Hata: {e}")
        return False

def main():
    # --- ADIM 0: SANAL ORTAM KONTROLÜ VE OLUŞTURMA ---
    if not os.path.exists("venv"):
        print("📦 Sanal ortam (venv) bulunamadı. Oluşturuluyor...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    if not is_venv():
        print("🔄 Sanal ortam üzerinden yeniden başlatılıyor...")
        # Arch Linux uyumlu venv python yolu
        python_executable = os.path.join("venv", "bin", "python")
        subprocess.run([python_executable] + sys.argv)
        # İşlem bittiğinde kullanıcıyı aktif venv ile bir kabuğa sok
        print("\n✨ Kurulum bitti. Sanal ortam aktif bir şekilde kabuk açılıyor...")
        subprocess.run(["bash", "--rcfile", "venv/bin/activate"], check=False)
        sys.exit()

    # --- SCRIPTİN KALAN KISMI VENV İÇİNDE ÇALIŞIR ---
    try:
        # ADIM 1: GITHUB
        print_header(1, "GitHub Private Repo Hazırlığı")
        webbrowser.open("https://github.com/new")
        print("👉 GitHub'da 'Private' bir repo aç ve ismini kopyala.")
        
        github_username = input("\n👉 Kullanıcı Adın: ").strip()
        repo_name = input("👉 Açtığın Repo Adı: ").strip().lower().replace(" ", "-")
        project_folder = input("👉 Django Klasör Adı (Örn: core): ").strip() or "core"
        
        base_domain = f"{repo_name}.vercel.app"
        repo_url = f"https://github.com/{github_username}/{repo_name}.git"

        # ADIM 2: NEON VE RECAPTCHA
        print_header(2, "Veritabanı ve Güvenlik")
        webbrowser.open("https://console.neon.tech/")
        db_url = input("👉 Neon DATABASE_URL: ").strip()
        
        webbrowser.open("https://www.google.com/recaptcha/admin/create")
        recaptcha_public = input("👉 reCAPTCHA Site Key: ").strip()
        recaptcha_private = input("👉 reCAPTCHA Secret Key: ").strip()

        # ADIM 3: CONFIG ÜRETİMİ
        print_header(3, "Dosya Yapılandırması")
        
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

        # ADIM 4: MIGRATION & ADMIN (VENV İÇİNDE)
        print_header(4, "Neon Tablo ve Admin İnşası")
        run_command("pip install -r requirements.txt", "Paketler kuruluyor")
        run_command("python manage.py makemigrations", "Migration hazırlığı")
        run_command("python manage.py migrate", "Neon'a yazılıyor")
        run_command("python manage.py createsuperuser", "Admin hesabı", interactive=True)

        # ADIM 5: GITHUB PUSH
        print_header(5, "GitHub'a Aktarım")
        if os.path.exists(".git"):
            import shutil
            shutil.rmtree(".git")
        
        git_cmds = [
            "git init",
            "git add .",
            'git commit -m "🚀 Automated setup with venv support"',
            "git branch -M main",
            f"git remote add origin {repo_url}",
            "git push -u origin main --force"
        ]
        for cmd in git_cmds: run_command(cmd, f"Git: {cmd}")

        # ADIM 6: FİNAL
        print_header(6, "Kurulum Tamamlandı!")
        print(f"👉 Vercel Keyler:\n- DATABASE_URL: {db_url}\n- ALLOWED_HOSTS: localhost,127.0.0.1,{base_domain},.vercel.app")
        webbrowser.open(f"https://vercel.com/new/import?s={repo_url}")
        
        print("\n✅ İşlem bitti. Seni aktif venv ortamına bırakıyorum...")
        # Bashrc yerine venv activate dosyasını kaynak alarak yeni bir kabuk açar
        subprocess.run(["bash", "--rcfile", "venv/bin/activate"], check=False)

    except KeyboardInterrupt:
        print("\n❌ İptal edildi.")

if __name__ == "__main__":
    main()