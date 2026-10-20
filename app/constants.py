"""Daftar pilihan yang dipakai di banyak tempat (form, filter, validasi).

Jika ingin menambah kategori, ubah juga CHECK pada database/schema.sql
(dan hapus file database lama agar tabelnya dibuat ulang).
"""

KATEGORI = ["Fasilitas", "Kebersihan", "Pelayanan", "Pembelajaran", "Lainnya"]
JENIS = ["Pengaduan", "Saran"]
STATUS = ["Menunggu", "Diproses", "Selesai"]
