-- Skema database AduSekolah (SQLite).
-- File ini dijalankan otomatis setiap aplikasi dimulai.
-- "IF NOT EXISTS" membuat data lama tidak terhapus.

-- Tabel akun admin. Yang disimpan adalah HASH password, bukan password asli.
CREATE TABLE IF NOT EXISTS admin (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    dibuat_pada   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Tabel laporan pengaduan dan saran.
CREATE TABLE IF NOT EXISTS laporan (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor_laporan   TEXT    UNIQUE,
    nama_pelapor    TEXT    NOT NULL,
    jenis           TEXT    NOT NULL DEFAULT 'Pengaduan'
                            CHECK (jenis IN ('Pengaduan', 'Saran')),
    kategori        TEXT    NOT NULL
                            CHECK (kategori IN ('Fasilitas', 'Kebersihan', 'Pelayanan', 'Pembelajaran', 'Lainnya')),
    judul           TEXT    NOT NULL,
    deskripsi       TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'Menunggu'
                            CHECK (status IN ('Menunggu', 'Diproses', 'Selesai')),
    dibuat_pada     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    diperbarui_pada TEXT,
    -- Foreign key: admin terakhir yang mengubah status laporan.
    -- Jika akun admin dihapus, kolom ini otomatis menjadi NULL.
    diperbarui_oleh INTEGER REFERENCES admin (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_laporan_status   ON laporan (status);
CREATE INDEX IF NOT EXISTS idx_laporan_kategori ON laporan (kategori);
CREATE INDEX IF NOT EXISTS idx_laporan_dibuat   ON laporan (dibuat_pada);
