"""Membuat akun admin pertama (atau mengganti password admin).

Cara pakai (di terminal, folder utama project):
    python create_admin.py

Password diketik tanpa tampil di layar, lalu disimpan dalam bentuk HASH.
Password asli tidak pernah disimpan di database maupun di file mana pun.
"""
import getpass
import sys

from app import create_app, models
from app.database import init_db
from app.security import buat_hash_password
from app.validators import validasi_akun_admin


def simpan_admin(username, password):
    """Membuat admin baru atau mengganti password admin yang sudah ada.

    Harus dipanggil di dalam app context. Mengembalikan "dibuat" atau "diperbarui".
    Melempar ValueError jika username/password tidak memenuhi syarat.
    """
    username, errors = validasi_akun_admin(username, password)
    if errors:
        raise ValueError(" ".join(errors))

    init_db()
    hash_password = buat_hash_password(password)
    if models.cari_admin(username):
        models.ganti_password_admin(username, hash_password)
        return "diperbarui"
    models.buat_admin(username, hash_password)
    return "dibuat"


def main():
    app = create_app()
    with app.app_context():
        print("=== Buat / ganti akun admin AduSekolah ===")
        username = input("Username admin : ").strip().lower()

        if models.cari_admin(username):
            jawab = input(f"Username '{username}' sudah ada. Ganti passwordnya? (y/n): ").strip().lower()
            if jawab != "y":
                print("Dibatalkan. Tidak ada yang diubah.")
                return

        password = getpass.getpass("Password (min. 8 karakter, tidak tampil di layar): ")
        ulangi = getpass.getpass("Ulangi password : ")
        if password != ulangi:
            print("GAGAL: kedua password tidak sama.")
            sys.exit(1)

        try:
            hasil = simpan_admin(username, password)
        except ValueError as error:
            print(f"GAGAL: {error}")
            sys.exit(1)

        print(f"Berhasil! Akun admin '{username.strip().lower()}' {hasil}. Silakan login di /admin/login")


if __name__ == "__main__":
    main()
