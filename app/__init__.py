"""Pabrik aplikasi (application factory) AduSekolah.

Fungsi create_app() merakit semua bagian: konfigurasi, database,
route (halaman), pengaman, dan halaman error.
"""
from datetime import datetime

from flask import Flask, g, render_template, request, session

from config import Config

from . import models
from .constants import JENIS, KATEGORI, STATUS
from .database import close_db, init_db
from .routes import admin, public
from .security import buat_csrf_token, periksa_csrf

BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

PESAN_ERROR = {
    400: ("Permintaan tidak valid",
          "Sesi formulir sudah kedaluwarsa atau datanya tidak lengkap. Kembali, muat ulang halaman, lalu coba lagi."),
    403: ("Akses ditolak", "Anda tidak memiliki izin untuk membuka halaman ini."),
    404: ("Halaman tidak ditemukan", "Alamat yang Anda buka tidak ada atau sudah dipindahkan."),
    405: ("Metode tidak diizinkan", "Halaman ini tidak bisa diakses dengan cara tersebut."),
    413: ("Data terlalu besar", "Teks yang dikirim terlalu panjang. Persingkat lalu coba lagi."),
    500: ("Terjadi kesalahan di server", "Maaf, ada masalah pada sistem. Silakan coba beberapa saat lagi."),
}


def _periksa_secret_key(secret_key):
    """Menghentikan aplikasi dengan pesan jelas jika SECRET_KEY belum diatur dengan benar."""
    if not secret_key or secret_key.startswith("ganti-dengan") or len(secret_key) < 16:
        raise RuntimeError(
            "SECRET_KEY belum diatur dengan benar.\n"
            "1) Salin file .env.example menjadi .env\n"
            "2) Buat kunci acak:  python -c \"import secrets; print(secrets.token_hex(32))\"\n"
            "3) Tempel hasilnya pada baris SECRET_KEY= di file .env"
        )


def format_tanggal(nilai, dengan_jam=True):
    """Filter Jinja: '2026-10-20 18:05:00' -> '20 Okt 2026, 18:05'."""
    if not nilai:
        return "-"
    try:
        waktu = datetime.strptime(nilai, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return nilai
    teks = f"{waktu.day} {BULAN[waktu.month - 1]} {waktu.year}"
    return f"{teks}, {waktu:%H:%M}" if dengan_jam else teks


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    _periksa_secret_key(app.config.get("SECRET_KEY"))

    # Database: tutup koneksi di akhir request, buat tabel saat aplikasi mulai.
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    # Halaman-halaman website.
    app.register_blueprint(public.bp)
    app.register_blueprint(admin.bp)

    app.add_template_filter(format_tanggal, "tanggal")

    @app.before_request
    def sebelum_request():
        g.admin = None
        if request.endpoint == "static":
            return
        periksa_csrf()
        admin_id = session.get("admin_id")
        if admin_id:
            g.admin = models.ambil_admin(admin_id)
            if g.admin is None:  # akun admin sudah dihapus dari database
                session.pop("admin_id", None)

    @app.context_processor
    def variabel_template():
        # Variabel ini otomatis tersedia di semua template.
        return {
            "csrf_token": buat_csrf_token,
            "nama_sekolah": app.config["NAMA_SEKOLAH"],
            "tahun": datetime.now().year,
            "daftar_kategori": KATEGORI,
            "daftar_jenis": JENIS,
            "daftar_status": STATUS,
        }

    @app.after_request
    def header_keamanan(respons):
        respons.headers.setdefault("X-Content-Type-Options", "nosniff")
        respons.headers.setdefault("X-Frame-Options", "DENY")
        respons.headers.setdefault("Referrer-Policy", "same-origin")
        if request.endpoint != "static":
            # Halaman tidak disimpan di cache browser (penting untuk halaman admin).
            respons.headers["Cache-Control"] = "no-store"
        return respons

    def tampilkan_error(error):
        kode = getattr(error, "code", 500) or 500
        judul, pesan = PESAN_ERROR.get(kode, PESAN_ERROR[500])
        return render_template("errors/error.html", kode=kode, judul=judul, pesan=pesan), kode

    for kode in PESAN_ERROR:
        app.register_error_handler(kode, tampilkan_error)

    return app
