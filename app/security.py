"""Fungsi keamanan: hash password, login admin, proteksi CSRF, dan batas percobaan login."""
import secrets
import time
from functools import wraps

from flask import abort, flash, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


# ---------------------------------------------------------------- Password

def buat_hash_password(password):
    """Mengubah password menjadi hash (tidak bisa dikembalikan ke password asli)."""
    # 600.000 putaran = rekomendasi OWASP untuk PBKDF2-SHA256.
    return generate_password_hash(password, method="pbkdf2:sha256:600000")


def cek_password(password_hash, password):
    return check_password_hash(password_hash, password)


# Hash palsu untuk dicocokkan saat username tidak ditemukan, supaya waktu
# respons login tetap sama dan penyerang tidak bisa menebak username yang valid.
HASH_PALSU = buat_hash_password("password-palsu-untuk-penyamaran")


# ------------------------------------------------------------- Login admin

def login_required(view):
    """Dekorator: halaman hanya bisa dibuka jika admin sudah login."""

    @wraps(view)
    def halaman_terlindungi(**kwargs):
        if g.get("admin") is None:
            flash("Silakan login sebagai admin terlebih dahulu.", "warning")
            tujuan = request.full_path.rstrip("?") if request.method == "GET" else None
            return redirect(url_for("admin.login", next=tujuan))
        return view(**kwargs)

    return halaman_terlindungi


def alamat_aman(tujuan):
    """True jika alamat tujuan adalah alamat di dalam website ini (bukan situs lain)."""
    return bool(tujuan) and tujuan.startswith("/") and not tujuan.startswith("//") and "\\" not in tujuan


class PembatasLogin:
    """Membatasi percobaan login yang gagal per alamat IP (disimpan di memori)."""

    def __init__(self, batas, jeda_detik):
        self.batas = batas
        self.jeda = jeda_detik
        self.catatan = {}

    def _waktu_aktif(self, kunci):
        sekarang = time.time()
        aktif = [t for t in self.catatan.get(kunci, []) if sekarang - t < self.jeda]
        self.catatan[kunci] = aktif
        return aktif

    def terkunci(self, kunci):
        return len(self._waktu_aktif(kunci)) >= self.batas

    def catat_gagal(self, kunci):
        self._waktu_aktif(kunci).append(time.time())

    def reset(self, kunci):
        self.catatan.pop(kunci, None)


# -------------------------------------------------------------------- CSRF
# CSRF = serangan yang menipu browser admin agar mengirim permintaan tanpa
# disadari. Setiap formulir POST wajib membawa token rahasia milik sesi.

def buat_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def periksa_csrf():
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return
    token_sesi = session.get("csrf_token", "")
    token_form = request.form.get("csrf_token", "")
    if not token_sesi or not secrets.compare_digest(token_sesi.encode(), token_form.encode()):
        abort(400)
