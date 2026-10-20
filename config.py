"""Pengaturan aplikasi AduSekolah.

Nilai rahasia (SECRET_KEY) dibaca dari environment variable atau file .env,
BUKAN ditulis langsung di dalam kode.
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Folder utama project (tempat file config.py ini berada).
BASE_DIR = Path(__file__).resolve().parent

# Membaca file .env (jika ada) ke dalam environment variable.
load_dotenv(BASE_DIR / ".env")


class Config:
    # Kunci rahasia untuk menandatangani cookie sesi login.
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    NAMA_SEKOLAH = os.environ.get("NAMA_SEKOLAH", "Sekolah Anda")

    # Lokasi file database SQLite dan file skema tabelnya.
    DATABASE = os.environ.get("DATABASE_PATH") or str(BASE_DIR / "database" / "adusekolah.db")
    SCHEMA_FILE = str(BASE_DIR / "database" / "schema.sql")

    # Batas ukuran data yang boleh dikirim (64 KB sudah sangat cukup untuk teks).
    MAX_CONTENT_LENGTH = 64 * 1024

    # Pengaturan keamanan cookie sesi.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # Jumlah laporan per halaman pada tabel admin.
    LAPORAN_PER_HALAMAN = 10

    # Perlindungan login: maksimal percobaan gagal per alamat IP.
    LOGIN_BATAS_GAGAL = 5
    LOGIN_JEDA_DETIK = 300
