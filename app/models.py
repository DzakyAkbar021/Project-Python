"""Semua query SQL ada di file ini.

Seluruh query memakai tanda tanya (?) sebagai tempat nilai (parameterized SQL),
sehingga input pengguna tidak pernah digabung langsung ke teks SQL.
Ini yang mencegah serangan SQL injection.
"""
from datetime import datetime

from .database import get_db


# ---------------------------------------------------------------- Laporan

def buat_laporan(nama_pelapor, jenis, kategori, judul, deskripsi):
    """Menyimpan laporan baru dan membuat nomor laporannya.

    Format nomor: ADU-TAHUNBULANTANGGAL-NOMORURUT, contoh ADU-20261020-0007.
    Mengembalikan (id, nomor_laporan).
    """
    db = get_db()
    with db:  # transaksi: kedua perintah berhasil bersama, atau dibatalkan bersama
        cur = db.execute(
            "INSERT INTO laporan (nama_pelapor, jenis, kategori, judul, deskripsi) "
            "VALUES (?, ?, ?, ?, ?)",
            (nama_pelapor, jenis, kategori, judul, deskripsi),
        )
        laporan_id = cur.lastrowid
        nomor = f"ADU-{datetime.now():%Y%m%d}-{laporan_id:04d}"
        db.execute("UPDATE laporan SET nomor_laporan = ? WHERE id = ?", (nomor, laporan_id))
    return laporan_id, nomor


def hitung_statistik():
    """Jumlah laporan: total, menunggu, diproses, selesai."""
    baris = get_db().execute(
        "SELECT COUNT(*) AS total, "
        "COALESCE(SUM(status = 'Menunggu'), 0) AS menunggu, "
        "COALESCE(SUM(status = 'Diproses'), 0) AS diproses, "
        "COALESCE(SUM(status = 'Selesai'), 0) AS selesai "
        "FROM laporan"
    ).fetchone()
    return dict(baris)


def _escape_like(teks):
    """Agar karakter % dan _ yang diketik pengguna dianggap huruf biasa."""
    return teks.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _bangun_filter(q, kategori, status):
    """Menyusun bagian WHERE. Teks SQL-nya tetap, nilainya lewat parameter."""
    kondisi, nilai = [], []
    if q:
        pola = f"%{_escape_like(q)}%"
        kondisi.append("(judul LIKE ? ESCAPE '\\' OR nomor_laporan LIKE ? ESCAPE '\\')")
        nilai += [pola, pola]
    if kategori:
        kondisi.append("kategori = ?")
        nilai.append(kategori)
    if status:
        kondisi.append("status = ?")
        nilai.append(status)
    where = (" WHERE " + " AND ".join(kondisi)) if kondisi else ""
    return where, nilai


def hitung_laporan(q="", kategori="", status=""):
    where, nilai = _bangun_filter(q, kategori, status)
    return get_db().execute(f"SELECT COUNT(*) FROM laporan{where}", nilai).fetchone()[0]


def cari_laporan(q="", kategori="", status="", halaman=1, per_halaman=10):
    where, nilai = _bangun_filter(q, kategori, status)
    offset = (halaman - 1) * per_halaman
    return get_db().execute(
        "SELECT id, nomor_laporan, nama_pelapor, jenis, kategori, judul, status, dibuat_pada "
        f"FROM laporan{where} ORDER BY id DESC LIMIT ? OFFSET ?",
        nilai + [per_halaman, offset],
    ).fetchall()


def laporan_terbaru(jumlah=5):
    return cari_laporan(halaman=1, per_halaman=jumlah)


def ambil_laporan(laporan_id):
    """Detail satu laporan, termasuk username admin yang terakhir mengubah status."""
    return get_db().execute(
        "SELECT l.*, a.username AS diperbarui_oleh_nama "
        "FROM laporan l LEFT JOIN admin a ON a.id = l.diperbarui_oleh "
        "WHERE l.id = ?",
        (laporan_id,),
    ).fetchone()


def ubah_status(laporan_id, status_baru, admin_id):
    """Mengubah status. Mengembalikan True jika laporannya ada."""
    db = get_db()
    with db:
        cur = db.execute(
            "UPDATE laporan SET status = ?, diperbarui_pada = datetime('now', 'localtime'), "
            "diperbarui_oleh = ? WHERE id = ?",
            (status_baru, admin_id, laporan_id),
        )
    return cur.rowcount > 0


def hapus_laporan(laporan_id):
    """Menghapus laporan. Mengembalikan True jika laporannya ada."""
    db = get_db()
    with db:
        cur = db.execute("DELETE FROM laporan WHERE id = ?", (laporan_id,))
    return cur.rowcount > 0


# ------------------------------------------------------------------ Admin

def cari_admin(username):
    return get_db().execute(
        "SELECT id, username, password_hash FROM admin WHERE username = ?", (username,)
    ).fetchone()


def ambil_admin(admin_id):
    return get_db().execute(
        "SELECT id, username FROM admin WHERE id = ?", (admin_id,)
    ).fetchone()


def buat_admin(username, password_hash):
    db = get_db()
    with db:
        db.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )


def ganti_password_admin(username, password_hash):
    db = get_db()
    with db:
        db.execute(
            "UPDATE admin SET password_hash = ? WHERE username = ?",
            (password_hash, username),
        )
