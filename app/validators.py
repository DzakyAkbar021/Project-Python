"""Validasi data dari formulir (dilakukan di server, bukan hanya di browser)."""
import re

from .constants import JENIS, KATEGORI

POLA_USERNAME = re.compile(r"^[a-z0-9_.-]{3,30}$")
MIN_PASSWORD = 8


def _satu_baris(teks):
    """Merapikan spasi berlebih: '  Budi   Santoso ' -> 'Budi Santoso'."""
    return " ".join((teks or "").split())


def _paragraf(teks):
    """Merapikan teks panjang, baris baru tetap dipertahankan."""
    return (teks or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def validasi_laporan(form):
    """Memeriksa isian form laporan.

    Mengembalikan (nilai, errors):
      nilai  = data yang sudah dirapikan (dipakai untuk mengisi ulang form)
      errors = kamus {nama_kolom: pesan_error}; kosong jika semuanya valid
    """
    nilai = {
        "nama_pelapor": _satu_baris(form.get("nama_pelapor")),
        "jenis": (form.get("jenis") or "").strip(),
        "kategori": (form.get("kategori") or "").strip(),
        "judul": _satu_baris(form.get("judul")),
        "deskripsi": _paragraf(form.get("deskripsi")),
    }
    errors = {}

    def cek_teks(kunci, label, minimal, maksimal):
        panjang = len(nilai[kunci])
        if panjang == 0:
            errors[kunci] = f"{label} wajib diisi."
        elif panjang < minimal:
            errors[kunci] = f"{label} minimal {minimal} karakter."
        elif panjang > maksimal:
            errors[kunci] = f"{label} maksimal {maksimal} karakter."

    cek_teks("nama_pelapor", "Nama pelapor", 2, 100)
    cek_teks("judul", "Judul laporan", 5, 150)
    cek_teks("deskripsi", "Deskripsi", 10, 2000)

    if nilai["jenis"] not in JENIS:
        errors["jenis"] = "Pilih jenis laporan: Pengaduan atau Saran."
    if not nilai["kategori"]:
        errors["kategori"] = "Kategori wajib dipilih."
    elif nilai["kategori"] not in KATEGORI:
        errors["kategori"] = "Kategori tidak valid."

    return nilai, errors


def validasi_akun_admin(username, password):
    """Memeriksa username dan password untuk akun admin baru.

    Mengembalikan (username_rapi, daftar_error).
    """
    username = (username or "").strip().lower()
    errors = []
    if not POLA_USERNAME.match(username):
        errors.append(
            "Username 3-30 karakter, hanya boleh huruf, angka, titik (.), garis bawah (_) atau minus (-)."
        )
    if len(password or "") < MIN_PASSWORD:
        errors.append(f"Password minimal {MIN_PASSWORD} karakter.")
    return username, errors
