"""
AnyPlace Ultimate Kurulum Sihirbazı
Tkinter tabanlı GUI — kullanıcı terminal görmeden Django projesi kurar.
"""

import os, sys, secrets, time, subprocess, webbrowser, json, shutil, threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.font import Font

# ─────────────────────────── RENKLER & STİL ───────────────────────────
BG        = "#0f0f14"
PANEL     = "#16161f"
CARD      = "#1e1e2e"
ACCENT    = "#7c6af7"
ACCENT2   = "#a78bfa"
SUCCESS   = "#4ade80"
WARNING   = "#fbbf24"
ERROR     = "#f87171"
TEXT      = "#e2e0f0"
SUBTEXT   = "#8b87a8"
BORDER    = "#2e2b45"
WHITE     = "#ffffff"

STEPS = [
    ("GitHub",      "🐙", "GitHub hesabın ve yeni bir private repo gerekiyor"),
    ("Veritabanı",  "🐘", "Neon.tech ücretsiz Postgres veritabanı"),
    ("reCAPTCHA",   "🛡️",  "Google reCAPTCHA güvenlik anahtarları"),
    ("Yapılandırma","⚙️",  "Dosyalar üretiliyor ve migration çalışıyor"),
    ("Admin Hesabı","👤", "Site yöneticisi (superuser) hesabı oluştur"),
    ("GitHub Push", "🚀", "Proje GitHub'a yükleniyor"),
    ("Tamamlandı",  "✅", "Vercel deploy için son adım"),
]

# ─────────────────────────── ANA PENCERE ──────────────────────────────
class SetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AnyPlace Kurulum Sihirbazı")
        self.geometry("900x680")
        self.minsize(820, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Veriler
        self.data = {}
        self.current_step = 0

        # Özel fontlar (sistem fontları kullanılıyor, tkinter'da harici font yok)
        self.font_title  = ("Georgia", 22, "bold")
        self.font_sub    = ("Georgia", 12, "italic")
        self.font_label  = ("Courier", 11, "bold")
        self.font_input  = ("Courier", 12)
        self.font_btn    = ("Georgia", 12, "bold")
        self.font_small  = ("Courier", 9)
        self.font_log    = ("Courier", 10)

        self._build_ui()
        self._show_step(0)

    # ── UI İSKELETİ ──
    def _build_ui(self):
        # Sol sidebar — adımlar
        self.sidebar = tk.Frame(self, bg=PANEL, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="ANYPLACE", fg=ACCENT2, bg=PANEL,
                 font=("Georgia", 16, "bold"), pady=20).pack()
        tk.Label(self.sidebar, text="Kurulum Sihirbazı", fg=SUBTEXT, bg=PANEL,
                 font=("Georgia", 9, "italic")).pack()

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=16)

        self.step_labels = []
        for i, (name, icon, _) in enumerate(STEPS):
            f = tk.Frame(self.sidebar, bg=PANEL, cursor="hand2")
            f.pack(fill="x", padx=12, pady=3)
            lbl = tk.Label(f, text=f"  {icon}  {name}", fg=SUBTEXT, bg=PANEL,
                           font=("Courier", 10), anchor="w", pady=8, padx=8)
            lbl.pack(fill="x")
            self.step_labels.append((f, lbl))

        # Sağ içerik alanı
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        # Üst başlık şeridi
        self.header_frame = tk.Frame(self.content, bg=CARD, height=100)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)

        self.lbl_step_num = tk.Label(self.header_frame, text="", fg=ACCENT, bg=CARD,
                                     font=("Courier", 10, "bold"), padx=30, pady=10)
        self.lbl_step_num.pack(anchor="w")

        self.lbl_title = tk.Label(self.header_frame, text="", fg=WHITE, bg=CARD,
                                  font=self.font_title, padx=30)
        self.lbl_title.pack(anchor="w")

        self.lbl_desc = tk.Label(self.header_frame, text="", fg=SUBTEXT, bg=CARD,
                                 font=self.font_sub, padx=30)
        self.lbl_desc.pack(anchor="w")

        # Orta form / log alanı
        self.form_frame = tk.Frame(self.content, bg=BG)
        self.form_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Alt butonlar
        btn_bar = tk.Frame(self.content, bg=CARD, height=60)
        btn_bar.pack(fill="x", side="bottom")
        btn_bar.pack_propagate(False)

        self.btn_back = tk.Button(btn_bar, text="← Geri", command=self._go_back,
                                  bg=PANEL, fg=SUBTEXT, font=self.font_btn,
                                  relief="flat", padx=20, pady=10, cursor="hand2",
                                  activebackground=BORDER, activeforeground=WHITE)
        self.btn_back.pack(side="left", padx=16, pady=10)

        self.btn_next = tk.Button(btn_bar, text="Devam →", command=self._go_next,
                                  bg=ACCENT, fg=WHITE, font=self.font_btn,
                                  relief="flat", padx=28, pady=10, cursor="hand2",
                                  activebackground=ACCENT2, activeforeground=WHITE)
        self.btn_next.pack(side="right", padx=16, pady=10)

        # İlerleme çubuğu
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Wizard.Horizontal.TProgressbar",
                        troughcolor=PANEL, background=ACCENT,
                        thickness=4, borderwidth=0)
        self.progress = ttk.Progressbar(self.content, style="Wizard.Horizontal.TProgressbar",
                                        maximum=len(STEPS), value=0)
        self.progress.pack(fill="x", side="bottom")

    # ── ADIM GEÇİŞLERİ ──
    def _show_step(self, idx):
        self.current_step = idx
        name, icon, desc = STEPS[idx]

        # Sidebar güncelle
        for i, (f, lbl) in enumerate(self.step_labels):
            if i < idx:
                lbl.config(fg=SUCCESS, bg=PANEL)
            elif i == idx:
                f.config(bg=ACCENT)
                lbl.config(fg=WHITE, bg=ACCENT)
            else:
                f.config(bg=PANEL)
                lbl.config(fg=SUBTEXT, bg=PANEL)

        # Başlık
        self.lbl_step_num.config(text=f"ADIM {idx + 1} / {len(STEPS)}")
        self.lbl_title.config(text=f"{icon}  {name}")
        self.lbl_desc.config(text=desc)
        self.progress["value"] = idx

        # Formu temizle
        for w in self.form_frame.winfo_children():
            w.destroy()

        # Buton durumları
        self.btn_back.config(state="normal" if idx > 0 else "disabled")

        # Adıma özel içerik
        builders = [
            self._step_github,
            self._step_neon,
            self._step_recaptcha,
            self._step_configure,
            self._step_superuser,
            self._step_git_push,
            self._step_done,
        ]
        builders[idx]()

    def _go_next(self):
        validators = [
            self._validate_github,
            self._validate_neon,
            self._validate_recaptcha,
            None,  # configure otomatik
            self._validate_superuser,
            None,  # git push otomatik
            None,  # done
        ]
        v = validators[self.current_step]
        if v and not v():
            return
        if self.current_step < len(STEPS) - 1:
            self._show_step(self.current_step + 1)

    def _go_back(self):
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    # ── YARDIMCI: Input widget ──
    def _make_field(self, parent, label, var, placeholder="", show=""):
        tk.Label(parent, text=label, fg=ACCENT2, bg=BG,
                 font=self.font_label, anchor="w").pack(fill="x", pady=(14, 2))
        entry = tk.Entry(parent, textvariable=var, font=self.font_input,
                         bg=CARD, fg=TEXT, insertbackground=ACCENT2,
                         relief="flat", show=show,
                         highlightthickness=1, highlightcolor=ACCENT,
                         highlightbackground=BORDER)
        entry.pack(fill="x", ipady=8, padx=0)
        if placeholder and not var.get():
            entry.insert(0, placeholder)
            entry.config(fg=SUBTEXT)
            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                    entry.config(fg=TEXT)
            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=SUBTEXT)
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        return entry

    def _make_link_btn(self, parent, text, url, icon="🔗"):
        def open_url():
            webbrowser.open(url)
        btn = tk.Button(parent, text=f"{icon}  {text}", command=open_url,
                        bg=PANEL, fg=ACCENT2, font=("Courier", 10),
                        relief="flat", padx=12, pady=6, cursor="hand2",
                        activebackground=BORDER, activeforeground=WHITE)
        btn.pack(anchor="w", pady=(4, 0))
        return btn

    def _make_info(self, parent, text):
        tk.Label(parent, text=text, fg=SUBTEXT, bg=BG,
                 font=("Courier", 10), anchor="w", justify="left",
                 wraplength=580).pack(fill="x", pady=(2, 0))

    # ── ADIM 1: GITHUB ──
    def _step_github(self):
        f = self.form_frame
        self._make_info(f, "Önce GitHub'da yeni bir PRIVATE repo oluştur, sonra bilgilerini gir.")
        self._make_link_btn(f, "GitHub'da yeni repo aç", "https://github.com/new", "🐙")

        self.var_gh_user = tk.StringVar(value=self.data.get("github_username", ""))
        self.var_gh_repo = tk.StringVar(value=self.data.get("repo_name", ""))
        self.var_gh_folder = tk.StringVar(value=self.data.get("project_folder", "core"))

        self._make_field(f, "GitHub Kullanıcı Adı", self.var_gh_user, "ornek: johndoe")
        self._make_field(f, "Repo Adı", self.var_gh_repo, "ornek: benim-sitem")
        self._make_field(f, "Django Klasör Adı", self.var_gh_folder, "ornek: core")

    def _validate_github(self):
        u = self.var_gh_user.get().strip()
        r = self.var_gh_repo.get().strip()
        f = self.var_gh_folder.get().strip()
        placeholders = ["ornek: johndoe", "ornek: benim-sitem", "ornek: core"]
        if not u or u in placeholders:
            messagebox.showwarning("Eksik Alan", "GitHub kullanıcı adını gir.")
            return False
        if not r or r in placeholders:
            messagebox.showwarning("Eksik Alan", "Repo adını gir.")
            return False
        self.data["github_username"] = u
        self.data["repo_name"] = r.lower().replace(" ", "-")
        self.data["project_folder"] = f or "core"
        self.data["base_domain"] = f"{self.data['repo_name']}.vercel.app"
        self.data["repo_url"] = f"https://github.com/{u}/{self.data['repo_name']}.git"
        return True

    # ── ADIM 2: NEON ──
    def _step_neon(self):
        f = self.form_frame
        self._make_info(f, "Neon.tech'de ücretsiz bir Postgres veritabanı oluştur.")
        self._make_info(f, "Dashboard > Connection Details > Connection String kopyala.")
        self._make_link_btn(f, "Neon Dashboard'u aç", "https://console.neon.tech/", "🐘")

        self.var_db_url = tk.StringVar(value=self.data.get("db_url", ""))
        self._make_field(f, "DATABASE_URL", self.var_db_url,
                         "postgresql://user:pass@host/dbname")

    def _validate_neon(self):
        url = self.var_db_url.get().strip()
        if not url or url == "postgresql://user:pass@host/dbname":
            messagebox.showwarning("Eksik Alan", "DATABASE_URL'i yapıştır.")
            return False
        if not url.startswith("postgres"):
            messagebox.showwarning("Hatalı Format", "URL 'postgresql://' ile başlamalı.")
            return False
        self.data["db_url"] = url
        return True

    # ── ADIM 3: RECAPTCHA ──
    def _step_recaptcha(self):
        f = self.form_frame
        domain     = self.data.get("base_domain", "<repo>.vercel.app")
        www_domain = f"www.{domain}"

        self._make_info(f, "Google reCAPTCHA kayıt sayfasında her iki domaini de eklemen gerekiyor:")

        # Domain kutuları — kopyalanabilir
        for d in [domain, www_domain]:
            row = tk.Frame(f, bg=CARD, padx=12, pady=6,
                           highlightthickness=1, highlightbackground=BORDER)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="🔗", bg=CARD, fg=ACCENT2,
                     font=("Courier", 11)).pack(side="left", padx=(0, 8))
            tk.Label(row, text=d, bg=CARD, fg=TEXT,
                     font=("Courier", 11, "bold")).pack(side="left", fill="x", expand=True)

            def make_copy(val):
                def _copy():
                    self.clipboard_clear()
                    self.clipboard_append(val)
                return _copy
            tk.Button(row, text="📋 Kopyala", command=make_copy(d),
                      bg=PANEL, fg=ACCENT2, font=("Courier", 9),
                      relief="flat", cursor="hand2",
                      activebackground=BORDER).pack(side="right")

        self._make_link_btn(f, "reCAPTCHA Yönetim Paneli",
                            "https://www.google.com/recaptcha/admin/create", "🛡️")
        self._make_info(f, "Panelde 'reCAPTCHA v2 — Checkbox' seçmeyi unutma.")

        self.var_rc_pub = tk.StringVar(value=self.data.get("recaptcha_public", ""))
        self.var_rc_prv = tk.StringVar(value=self.data.get("recaptcha_private", ""))

        self._make_field(f, "Site Key (Public)", self.var_rc_pub, "6Lc...")
        self._make_field(f, "Secret Key (Private)", self.var_rc_prv, "6Lc...", show="•")

    def _validate_recaptcha(self):
        pub = self.var_rc_pub.get().strip()
        prv = self.var_rc_prv.get().strip()
        placeholders = ["6Lc..."]
        if not pub or pub in placeholders:
            messagebox.showwarning("Eksik Alan", "Site Key gir.")
            return False
        if not prv or prv in placeholders:
            messagebox.showwarning("Eksik Alan", "Secret Key gir.")
            return False
        self.data["recaptcha_public"] = pub
        self.data["recaptcha_private"] = prv
        return True

    # ── ADIM 4: YAPILANDIRMA ──
    def _step_configure(self):
        f = self.form_frame
        self.btn_next.config(state="disabled", text="Çalışıyor...")

        self.log_box = scrolledtext.ScrolledText(
            f, bg=CARD, fg=SUCCESS, font=self.font_log,
            relief="flat", state="disabled",
            highlightthickness=1, highlightbackground=BORDER)
        self.log_box.pack(fill="both", expand=True)

        threading.Thread(target=self._run_configure, daemon=True).start()

    def _log(self, msg, color=None):
        self.log_box.config(state="normal")
        tag = color or "default"
        self.log_box.tag_config(tag, foreground=color or SUCCESS)
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _venv_python(self):
        """Venv içindeki python ve pip yollarını döndür."""
        if os.name == "nt":
            return (os.path.join("venv", "Scripts", "python.exe"),
                    os.path.join("venv", "Scripts", "pip.exe"))
        return (os.path.join("venv", "bin", "python"),
                os.path.join("venv", "bin", "pip"))

    def _run_configure(self):
        try:
            d = self.data
            pf = d["project_folder"]
            python_exe, pip_exe = self._venv_python()

            # vercel.json
            self._log("📝 vercel.json oluşturuluyor...")
            with open("vercel.json", "w") as f:
                json.dump({
                    "version": 2,
                    "builds": [{"src": f"{pf}/wsgi.py", "use": "@vercel/python"}],
                    "routes": [{"src": "/(.*)", "dest": f"{pf}/wsgi.py"}]
                }, f, indent=2)
            self._log("✅ vercel.json hazır", SUCCESS)

            # .env
            self._log("🔑 .env dosyası oluşturuluyor...")
            secret_key = secrets.token_urlsafe(50)
            d["secret_key"] = secret_key
            env_content = (
                f'DJANGO_SECRET_KEY="{secret_key}"\n'
                f'DATABASE_URL="{d["db_url"]}"\n'
                f'DEBUG=True\n'
                f'ALLOWED_HOSTS="localhost,127.0.0.1,{d["base_domain"]},.vercel.app"\n'
                f'RECAPTCHA_PUBLIC_KEY="{d["recaptcha_public"]}"\n'
                f'RECAPTCHA_PRIVATE_KEY="{d["recaptcha_private"]}"\n'
            )
            with open(".env", "w") as f:
                f.write(env_content)
            self._log("✅ .env hazır", SUCCESS)

            # pip install — venv pip'i kullan
            self._log("📦 Kütüphaneler kuruluyor (requirements.txt)...")
            result = subprocess.run(
                [pip_exe, "install", "-r", "requirements.txt"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                self._log(f"⚠️ pip install uyarısı:\n{result.stderr[:200]}", WARNING)
            else:
                self._log("✅ Kütüphaneler kuruldu", SUCCESS)

            # migrate — venv python'unu kullan
            run_env = os.environ.copy()
            run_env["DATABASE_URL"] = d["db_url"]
            self._log("🐘 Neon veritabanı tabloları oluşturuluyor (migrate)...")
            result = subprocess.run(
                [python_exe, "manage.py", "migrate"],
                capture_output=True, text=True, env=run_env
            )
            if result.returncode != 0:
                self._log(f"❌ Migrate hatası:\n{result.stderr}", ERROR)
                self.after(0, lambda: messagebox.showerror(
                    "Migrate Hatası",
                    f"Hata:\n{result.stderr[:400]}\n\nDATABASE_URL'i kontrol et."
                ))
                self.after(0, lambda: self.btn_next.config(state="normal", text="Tekrar Dene →"))
                return
            self._log("✅ Tablolar oluşturuldu", SUCCESS)
            self._log("\n✅ Yapılandırma tamamlandı! Devam edebilirsin.", SUCCESS)
            self.after(0, lambda: self.btn_next.config(state="normal", text="Devam →"))

        except Exception as e:
            self._log(f"❌ Beklenmeyen hata: {e}", ERROR)
            self.after(0, lambda: self.btn_next.config(state="normal", text="Tekrar Dene →"))

    # ── ADIM 5: SUPERUSER ──
    def _step_superuser(self):
        f = self.form_frame
        self._make_info(f, "Site yönetim paneline giriş için bir admin hesabı oluştur.")
        self._make_info(f, "Bu bilgileri güvenli bir yere kaydet!")

        self.var_su_user  = tk.StringVar(value=self.data.get("su_username", ""))
        self.var_su_email = tk.StringVar(value=self.data.get("su_email", ""))
        self.var_su_pass1 = tk.StringVar()
        self.var_su_pass2 = tk.StringVar()

        self._make_field(f, "Kullanıcı Adı", self.var_su_user, "ornek: admin")
        self._make_field(f, "E-posta Adresi", self.var_su_email, "ornek: admin@example.com")
        self._make_field(f, "Şifre", self.var_su_pass1, "En az 8 karakter", show="•")
        self._make_field(f, "Şifre (Tekrar)", self.var_su_pass2, "Şifreyi tekrar gir", show="•")

        # Durum etiketi
        self.lbl_su_status = tk.Label(f, text="", fg=ERROR, bg=BG,
                                      font=("Courier", 10))
        self.lbl_su_status.pack(anchor="w", pady=(8, 0))

    def _validate_superuser(self):
        username = self.var_su_user.get().strip()
        email    = self.var_su_email.get().strip()
        p1       = self.var_su_pass1.get()
        p2       = self.var_su_pass2.get()
        placeholders = ["ornek: admin", "ornek: admin@example.com",
                        "En az 8 karakter", "Şifreyi tekrar gir"]

        if not username or username in placeholders:
            self.lbl_su_status.config(text="⚠ Kullanıcı adı boş olamaz.")
            return False
        if not email or email in placeholders or "@" not in email:
            self.lbl_su_status.config(text="⚠ Geçerli bir e-posta gir.")
            return False
        if len(p1) < 8 or p1 in placeholders:
            self.lbl_su_status.config(text="⚠ Şifre en az 8 karakter olmalı.")
            return False
        if p1 != p2:
            self.lbl_su_status.config(text="⚠ Şifreler eşleşmiyor.")
            return False

        # Django'nun manage.py ile superuser oluştur (--no-input ile env üzerinden)
        self.lbl_su_status.config(text="⏳ Hesap oluşturuluyor...", fg=WARNING)
        self.update()

        python_exe, _ = self._venv_python()
        env = os.environ.copy()
        env["DJANGO_SUPERUSER_USERNAME"] = username
        env["DJANGO_SUPERUSER_EMAIL"]    = email
        env["DJANGO_SUPERUSER_PASSWORD"] = p1
        env["DATABASE_URL"]              = self.data.get("db_url", "")

        result = subprocess.run(
            [python_exe, "manage.py", "createsuperuser", "--no-input"],
            capture_output=True, text=True, env=env
        )

        if result.returncode != 0:
            # Zaten varsa sorun değil
            if "already exists" in result.stderr or "already exists" in result.stdout:
                self.lbl_su_status.config(
                    text=f"ℹ️ '{username}' zaten mevcut, devam ediliyor.", fg=WARNING)
                self.data["su_username"] = username
                self.data["su_email"]    = email
                return True
            self.lbl_su_status.config(
                text=f"❌ Hata: {result.stderr.strip()[:120]}", fg=ERROR)
            return False

        self.lbl_su_status.config(
            text=f"✅ Admin hesabı '{username}' oluşturuldu!", fg=SUCCESS)
        self.data["su_username"] = username
        self.data["su_email"]    = email
        return True

    # ── ADIM 6: GIT PUSH ──
    def _step_git_push(self):
        f = self.form_frame
        self.btn_next.config(state="disabled", text="Yükleniyor...")

        self.log_box = scrolledtext.ScrolledText(
            f, bg=CARD, fg=SUCCESS, font=self.font_log,
            relief="flat", state="disabled",
            highlightthickness=1, highlightbackground=BORDER)
        self.log_box.pack(fill="both", expand=True)

        threading.Thread(target=self._run_git_push, daemon=True).start()

    def _run_git_push(self):
        d = self.data
        repo_url = d["repo_url"]

        cmds = [
            ("git init", "Git başlatılıyor"),
            ("git add .", "Dosyalar ekleniyor"),
            ('git commit -m "🚀 Production-ready setup"', "Commit oluşturuluyor"),
            ("git branch -M main", "Branch: main"),
            (f"git remote add origin {repo_url}", "Remote ekleniyor"),
            ("git push -u origin main --force", "GitHub'a yükleniyor"),
        ]

        if os.path.exists(".git"):
            self._log("🗑️ Eski .git temizleniyor...", WARNING)
            shutil.rmtree(".git")

        for cmd, desc in cmds:
            self._log(f"\n⏳ {desc}...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                self._log(result.stdout.strip())
            if result.returncode != 0:
                self._log(f"❌ Hata: {result.stderr.strip()}", ERROR)
                self.after(0, lambda: messagebox.showerror(
                    "Git Hatası",
                    f"Komut başarısız:\n{cmd}\n\nHata:\n{result.stderr[:300]}"
                ))
                self.after(0, lambda: self.btn_next.config(state="normal", text="Tekrar Dene →"))
                return
            self._log(f"✅ {desc} tamamlandı", SUCCESS)

        self._log("\n🎉 Tüm dosyalar GitHub'a yüklendi!", SUCCESS)
        self.after(0, lambda: self.btn_next.config(state="normal", text="Devam →"))

    # ── ADIM 6: TAMAMLANDI ──
    def _step_done(self):
        f = self.form_frame
        d = self.data
        self.btn_next.config(text="Vercel'e Deploy Et →",
                             command=self._open_vercel, state="normal")
        self.btn_back.config(state="disabled")

        # Büyük başarı mesajı
        tk.Label(f, text="🎉 Kurulum Tamamlandı!", fg=SUCCESS, bg=BG,
                 font=("Georgia", 20, "bold")).pack(pady=(10, 4))
        tk.Label(f, text="Vercel ortam değişkenlerini eklemek için aşağıdaki bilgileri kopyala.",
                 fg=SUBTEXT, bg=BG, font=("Courier", 10)).pack(pady=(0, 14))

        # Anahtar kutusu
        box = tk.Frame(f, bg=CARD, padx=20, pady=16,
                       highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="x")

        keys = [
            ("DATABASE_URL",       d.get("db_url", "")),
            ("DJANGO_SECRET_KEY",  d.get("secret_key", "")),
            ("RECAPTCHA_PUBLIC_KEY",  d.get("recaptcha_public", "")),
            ("RECAPTCHA_PRIVATE_KEY", d.get("recaptcha_private", "")),
            ("DEBUG",              "False"),
            ("ALLOWED_HOSTS",      f"*.vercel.app,{d.get('base_domain','')}"),
        ]

        for k, v in keys:
            row = tk.Frame(box, bg=CARD)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{k}:", fg=ACCENT2, bg=CARD,
                     font=("Courier", 10, "bold"), width=26, anchor="w").pack(side="left")
            val_var = tk.StringVar(value=v)
            entry = tk.Entry(row, textvariable=val_var, font=("Courier", 10),
                             bg=PANEL, fg=TEXT, relief="flat",
                             readonlybackground=PANEL, state="readonly")
            entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(6, 0))

            def make_copy(val):
                def _copy():
                    self.clipboard_clear()
                    self.clipboard_append(val)
                return _copy
            tk.Button(row, text="📋", command=make_copy(v),
                      bg=PANEL, fg=ACCENT, font=("Courier", 10),
                      relief="flat", cursor="hand2",
                      activebackground=BORDER).pack(side="left", padx=4)

        tk.Label(f, text=f"Admin paneli: https://{d.get('base_domain','')}/admin",
                 fg=ACCENT2, bg=BG, font=("Courier", 11, "bold")).pack(anchor="w", pady=(8,0))
        tk.Label(f, text=f"Kullanıcı adı: {d.get('su_username', '-')}",
                 fg=SUBTEXT, bg=BG, font=("Courier", 10)).pack(anchor="w")

    def _open_vercel(self):
        repo_url = self.data.get("repo_url", "")
        webbrowser.open(f"https://vercel.com/new/import?s={repo_url}")


# ─────────────────────────── GİRİŞ NOKTASI ──────────────────────────
def check_venv():
    """Venv yoksa oluştur, requirements.txt'i kur, sonra venv içinde yeniden başlat."""
    if not os.path.exists("venv"):
        print("📦 Sanal ortam (venv) oluşturuluyor...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

    in_venv = (hasattr(sys, 'real_prefix') or
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

    if not in_venv:
        # Platform'a göre venv yolları
        if os.name == "nt":
            python_exe = os.path.join("venv", "Scripts", "python.exe")
            pip_exe    = os.path.join("venv", "Scripts", "pip.exe")
        else:
            python_exe = os.path.join("venv", "bin", "python")
            pip_exe    = os.path.join("venv", "bin", "pip")

        # requirements.txt varsa venv içinde kur (Django dahil her şey burada yüklenir)
        if os.path.exists("requirements.txt"):
            print("📦 Gerekli kütüphaneler kuruluyor (requirements.txt)...")
            result = subprocess.run([pip_exe, "install", "-r", "requirements.txt"])
            if result.returncode != 0:
                print("⚠️  Bazı paketler kurulamadı, devam ediliyor...")
        else:
            print("⚠️  requirements.txt bulunamadı, atlanıyor.")

        print("🔄 Sanal ortam içinde yeniden başlatılıyor...")
        os.execv(python_exe, [python_exe] + sys.argv)


if __name__ == "__main__":
    check_venv()
    app = SetupWizard()
    app.mainloop()