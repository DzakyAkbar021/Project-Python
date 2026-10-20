"""Koneksi ke database SQLite."""
import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    """Mengambil koneksi database untuk request yang sedang berjalan."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        # Hasil query bisa dibaca dengan nama kolom: baris["judul"]
        g.db.row_factory = sqlite3.Row
        # SQLite tidak mengaktifkan foreign key secara otomatis.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    """Menutup koneksi database di akhir request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Membuat folder database dan tabel-tabelnya jika belum ada."""
    folder_db = Path(current_app.config["DATABASE"]).parent
    folder_db.mkdir(parents=True, exist_ok=True)

    file_skema = Path(current_app.config["SCHEMA_FILE"])
    if not file_skema.exists():
        raise RuntimeError(
            f"File skema database tidak ditemukan: {file_skema}\n"
            "Pastikan folder 'database' dan file 'schema.sql' ada di folder utama project."
        )

    db = get_db()
    db.executescript(file_skema.read_text(encoding="utf-8"))
    db.commit()
