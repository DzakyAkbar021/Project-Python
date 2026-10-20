"""Tes otomatis AduSekolah.

Menjalankan semua tes (dari folder utama project):
    python -m unittest discover -s tests -t . -v

Tes memakai database sementara, jadi data asli Anda tidak tersentuh.
"""
import os
import sqlite3
import tempfile
import unittest

from app import create_app, models
from app.routes import admin as rute_admin
from create_admin import simpan_admin

PASSWORD = "PasswordKuat123"


class DasarTes(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.folder.name, "tes.db")
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "kunci-khusus-pengujian-123456",
            "DATABASE": self.db_path,
        })
        rute_admin.pembatas_login.catatan.clear()
        with self.app.app_context():
            simpan_admin("admin", PASSWORD)
        self.client = self.app.test_client()

    def tearDown(self):
        self.folder.cleanup()

    # ---- fungsi bantu
    def token(self, url):
        """Membuka halaman agar sesi punya token CSRF, lalu mengambil tokennya."""
        self.client.get(url)
        with self.client.session_transaction() as sesi:
            return sesi["csrf_token"]

    def kirim(self, **ubah):
        data = {
            "jenis": "Pengaduan", "nama_pelapor": "Budi Santoso", "kategori": "Fasilitas",
            "judul": "AC kelas XI RPL 1 rusak", "deskripsi": "AC di kelas sudah tidak dingin sejak dua minggu.",
        }
        data.update(ubah)
        data["csrf_token"] = self.token("/lapor")
        return self.client.post("/lapor", data=data)

    def login(self, username="admin", password=PASSWORD, tujuan=""):
        token = self.token("/admin/login")
        return self.client.post("/admin/login", data={
            "username": username, "password": password, "csrf_token": token, "next": tujuan})

    def jalankan_sql(self, sql, params=()):
        koneksi = sqlite3.connect(self.db_path)
        try:
            return koneksi.execute(sql, params).fetchall()
        finally:
            koneksi.close()

    def isi_laporan(self, jumlah, **kolom):
        with self.app.app_context():
            for i in range(jumlah):
                models.buat_laporan(
                    kolom.get("nama", f"Siswa {i}"), kolom.get("jenis", "Pengaduan"),
                    kolom.get("kategori", "Kebersihan"), kolom.get("judul", f"Laporan nomor {i}"),
                    "Deskripsi laporan percobaan.")


class TesPengunjung(DasarTes):
    def test_beranda_dan_form_terbuka(self):
        beranda = self.client.get("/")
        self.assertEqual(beranda.status_code, 200)
        self.assertIn("AduSekolah", beranda.get_data(as_text=True))
        form = self.client.get("/lapor")
        self.assertEqual(form.status_code, 200)
        halaman = form.get_data(as_text=True)
        for kategori in ["Fasilitas", "Kebersihan", "Pelayanan", "Pembelajaran", "Lainnya"]:
            self.assertIn(kategori, halaman)

    def test_kolom_kosong_ditolak(self):
        respons = self.kirim(nama_pelapor="", judul="", deskripsi="")
        self.assertEqual(respons.status_code, 400)
        halaman = respons.get_data(as_text=True)
        self.assertIn("Nama pelapor wajib diisi.", halaman)
        self.assertIn("Judul laporan wajib diisi.", halaman)
        self.assertIn("Deskripsi wajib diisi.", halaman)
        self.assertEqual(self.jalankan_sql("SELECT COUNT(*) FROM laporan")[0][0], 0)

    def test_hanya_spasi_ditolak(self):
        respons = self.kirim(nama_pelapor="     ", judul="      ", deskripsi="       \n   ")
        self.assertEqual(respons.status_code, 400)

    def test_kategori_dan_jenis_tidak_valid_ditolak(self):
        self.assertEqual(self.kirim(kategori="Hacker").status_code, 400)
        self.assertEqual(self.kirim(kategori="").status_code, 400)
        self.assertEqual(self.kirim(jenis="Spam").status_code, 400)

    def test_batas_panjang(self):
        self.assertEqual(self.kirim(judul="abc").status_code, 400)
        self.assertEqual(self.kirim(deskripsi="pendek").status_code, 400)
        self.assertEqual(self.kirim(deskripsi="x" * 2001).status_code, 400)

    def test_isian_dipertahankan_saat_error(self):
        respons = self.kirim(judul="Judul tetap ada", deskripsi="")
        self.assertIn("Judul tetap ada", respons.get_data(as_text=True))

    def test_kirim_laporan_berhasil_dan_nomor_tampil(self):
        respons = self.kirim()
        self.assertEqual(respons.status_code, 302)
        self.assertTrue(respons.headers["Location"].endswith("/lapor/berhasil"))
        halaman = self.client.get("/lapor/berhasil").get_data(as_text=True)
        self.assertIn("berhasil dikirim", halaman)
        nomor = self.jalankan_sql("SELECT nomor_laporan FROM laporan")[0][0]
        self.assertRegex(nomor, r"^ADU-\d{8}-0001$")
        self.assertIn(nomor, halaman)
        # Nomor hanya tampil sekali; membuka ulang diarahkan ke form.
        ulang = self.client.get("/lapor/berhasil")
        self.assertEqual(ulang.status_code, 302)
        # Isi laporan tidak bocor di halaman berhasil.
        self.assertNotIn("AC kelas XI RPL 1 rusak", halaman)

    def test_nomor_laporan_unik_berurutan(self):
        self.kirim()
        self.kirim(judul="Toilet lantai dua kotor")
        nomor = [b[0] for b in self.jalankan_sql("SELECT nomor_laporan FROM laporan ORDER BY id")]
        self.assertEqual(len(set(nomor)), 2)
        self.assertTrue(nomor[0].endswith("-0001") and nomor[1].endswith("-0002"))

    def test_buka_halaman_berhasil_tanpa_kirim_diarahkan(self):
        self.assertEqual(self.client.get("/lapor/berhasil").status_code, 302)

    def test_data_laporan_tidak_tampil_di_halaman_publik(self):
        self.kirim(judul="Judul Rahasia Pelapor", deskripsi="Isi sangat rahasia dan pribadi.")
        for alamat in ["/", "/lapor", "/lapor/berhasil", "/laporan", "/admin/laporan/1"]:
            halaman = self.client.get(alamat, follow_redirects=True).get_data(as_text=True)
            self.assertNotIn("Judul Rahasia Pelapor", halaman, alamat)
            self.assertNotIn("Isi sangat rahasia", halaman, alamat)


class TesKeamananForm(DasarTes):
    def test_post_tanpa_csrf_ditolak(self):
        respons = self.client.post("/lapor", data={
            "jenis": "Pengaduan", "nama_pelapor": "Budi", "kategori": "Fasilitas",
            "judul": "Judul percobaan", "deskripsi": "Deskripsi percobaan lengkap."})
        self.assertEqual(respons.status_code, 400)
        self.assertEqual(self.jalankan_sql("SELECT COUNT(*) FROM laporan")[0][0], 0)

    def test_csrf_salah_ditolak(self):
        self.token("/lapor")
        respons = self.client.post("/lapor", data={"csrf_token": "salah"})
        self.assertEqual(respons.status_code, 400)

    def test_xss_di_escape(self):
        self.kirim(judul="<script>alert(1)</script> judul", deskripsi="<img src=x onerror=alert(2)> isi laporan")
        self.login()
        daftar = self.client.get("/admin/laporan").get_data(as_text=True)
        detail = self.client.get("/admin/laporan/1").get_data(as_text=True)
        for halaman in (daftar, detail):
            self.assertNotIn("<script>alert(1)</script>", halaman)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", detail)
        self.assertNotIn("<img src=x", detail)

    def test_sql_injection_di_form_disimpan_sebagai_teks(self):
        self.kirim(judul="'); DROP TABLE laporan;-- ", nama_pelapor="Robert'); DROP TABLE admin;--")
        self.assertEqual(self.jalankan_sql("SELECT COUNT(*) FROM laporan")[0][0], 1)
        self.assertEqual(self.jalankan_sql("SELECT COUNT(*) FROM admin")[0][0], 1)

    def test_header_keamanan(self):
        respons = self.client.get("/")
        self.assertEqual(respons.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(respons.headers["X-Frame-Options"], "DENY")
        self.assertIn("no-store", respons.headers["Cache-Control"])

    def test_halaman_tidak_ada(self):
        respons = self.client.get("/halaman-tidak-ada")
        self.assertEqual(respons.status_code, 404)
        self.assertIn("Halaman tidak ditemukan", respons.get_data(as_text=True))

    def test_secret_key_wajib(self):
        for kunci in ("", "ganti-dengan-kunci-acak-yang-panjang", "pendek"):
            with self.assertRaises(RuntimeError):
                create_app({"SECRET_KEY": kunci, "DATABASE": self.db_path})


class TesLoginAdmin(DasarTes):
    def test_halaman_admin_butuh_login(self):
        self.isi_laporan(1)
        for alamat in ["/admin/", "/admin/laporan", "/admin/laporan/1"]:
            respons = self.client.get(alamat)
            self.assertEqual(respons.status_code, 302, alamat)
            self.assertIn("/admin/login", respons.headers["Location"])

    def test_aksi_ubah_dan_hapus_butuh_login(self):
        self.isi_laporan(1)
        token = self.token("/lapor")
        ubah = self.client.post("/admin/laporan/1/status", data={"status": "Selesai", "csrf_token": token})
        hapus = self.client.post("/admin/laporan/1/hapus", data={"csrf_token": token})
        self.assertEqual(ubah.status_code, 302)
        self.assertEqual(hapus.status_code, 302)
        self.assertIn("/admin/login", ubah.headers["Location"])
        baris = self.jalankan_sql("SELECT status FROM laporan WHERE id = 1")
        self.assertEqual(baris, [("Menunggu",)])

    def test_aksi_admin_butuh_csrf(self):
        self.isi_laporan(1)
        self.login()
        respons = self.client.post("/admin/laporan/1/hapus", data={})
        self.assertEqual(respons.status_code, 400)
        self.assertEqual(self.jalankan_sql("SELECT COUNT(*) FROM laporan")[0][0], 1)

    def test_logout_wajib_post(self):
        self.login()
        self.assertEqual(self.client.get("/admin/logout").status_code, 405)

    def test_password_tidak_disimpan_polos(self):
        hash_tersimpan = self.jalankan_sql("SELECT password_hash FROM admin")[0][0]
        self.assertNotEqual(hash_tersimpan, PASSWORD)
        self.assertNotIn(PASSWORD, hash_tersimpan)
        self.assertTrue(hash_tersimpan.startswith("pbkdf2:sha256:"))

    def test_login_salah(self):
        self.assertEqual(self.login(password="salah-total").status_code, 401)
        self.assertEqual(self.login(username="tidak-ada").status_code, 401)
        self.assertIn("/admin/login", self.client.get("/admin/").headers["Location"])

    def test_login_benar_logout(self):
        respons = self.login()
        self.assertEqual(respons.status_code, 302)
        self.assertTrue(respons.headers["Location"].endswith("/admin/"))
        dashboard = self.client.get("/admin/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertIn("Dashboard", dashboard.get_data(as_text=True))
        with self.client.session_transaction() as sesi:
            token = sesi["csrf_token"]
        keluar = self.client.post("/admin/logout", data={"csrf_token": token})
        self.assertEqual(keluar.status_code, 302)
        self.assertEqual(self.client.get("/admin/").status_code, 302)

    def test_username_tidak_peka_huruf_besar(self):
        self.assertEqual(self.login(username="  ADMIN ").status_code, 302)

    def test_next_aman(self):
        for tujuan in ["//evil.example.com", "https://evil.example.com", "/\\evil.example.com"]:
            self.client = self.app.test_client()
            respons = self.login(tujuan=tujuan)
            self.assertTrue(respons.headers["Location"].endswith("/admin/"), tujuan)
        self.client = self.app.test_client()
        respons = self.login(tujuan="/admin/laporan?status=Selesai")
        self.assertTrue(respons.headers["Location"].endswith("/admin/laporan?status=Selesai"))

    def test_batas_percobaan_login(self):
        for _ in range(5):
            self.assertEqual(self.login(password="salah").status_code, 401)
        self.assertEqual(self.login(password="salah").status_code, 429)
        # Walau password benar, tetap terkunci selama masa jeda.
        self.assertEqual(self.login().status_code, 429)

    def test_sql_injection_di_login(self):
        self.assertEqual(self.login(username="admin' OR '1'='1' --", password="x").status_code, 401)
        self.assertEqual(self.login(username="admin", password="' OR '1'='1").status_code, 401)

    def test_akun_dihapus_otomatis_logout(self):
        self.login()
        koneksi = sqlite3.connect(self.db_path)
        koneksi.execute("DELETE FROM admin")
        koneksi.commit()
        koneksi.close()
        self.assertEqual(self.client.get("/admin/").status_code, 302)


class TesFiturAdmin(DasarTes):
    def setUp(self):
        super().setUp()
        self.login()

    def test_dashboard_statistik(self):
        self.isi_laporan(3)
        koneksi = sqlite3.connect(self.db_path)
        koneksi.execute("UPDATE laporan SET status = 'Diproses' WHERE id = 2")
        koneksi.execute("UPDATE laporan SET status = 'Selesai' WHERE id = 3")
        koneksi.commit()
        koneksi.close()
        with self.app.app_context():
            self.assertEqual(models.hitung_statistik(),
                             {"total": 3, "menunggu": 1, "diproses": 1, "selesai": 1})
        halaman = self.client.get("/admin/").get_data(as_text=True)
        for teks in ["Total Laporan", "Menunggu", "Diproses", "Selesai", "Laporan terbaru"]:
            self.assertIn(teks, halaman)

    def test_dashboard_kosong(self):
        halaman = self.client.get("/admin/")
        self.assertEqual(halaman.status_code, 200)
        self.assertIn("Belum ada laporan", halaman.get_data(as_text=True))

    def test_daftar_semua_laporan(self):
        self.isi_laporan(3)
        halaman = self.client.get("/admin/laporan").get_data(as_text=True)
        self.assertIn("3 laporan ditemukan", halaman)
        self.assertEqual(halaman.count('data-nomor="'), 3)

    def test_cari_berdasarkan_judul_dan_nomor(self):
        self.isi_laporan(1, judul="Toilet lantai dua bau")
        self.isi_laporan(1, judul="Proyektor rusak")
        halaman = self.client.get("/admin/laporan?q=toilet").get_data(as_text=True)
        self.assertIn("Toilet lantai dua bau", halaman)
        self.assertNotIn("Proyektor rusak", halaman)
        halaman = self.client.get("/admin/laporan?q=-0002").get_data(as_text=True)
        self.assertIn("Proyektor rusak", halaman)
        self.assertNotIn("Toilet lantai dua bau", halaman)
        self.assertIn("0 laporan ditemukan", self.client.get("/admin/laporan?q=tidakadaapapun").get_data(as_text=True))

    def test_pencarian_karakter_khusus_aman(self):
        self.isi_laporan(2)
        # % dan _ dianggap huruf biasa, bukan wildcard
        self.assertIn("0 laporan ditemukan", self.client.get("/admin/laporan?q=%25").get_data(as_text=True))
        self.assertIn("0 laporan ditemukan", self.client.get("/admin/laporan?q=_").get_data(as_text=True))
        # Percobaan SQL injection tidak merusak apa pun
        halaman = self.client.get("/admin/laporan?q=' OR 1=1 --")
        self.assertEqual(halaman.status_code, 200)
        self.assertIn("0 laporan ditemukan", halaman.get_data(as_text=True))
        self.client.get("/admin/laporan?q=x'; DROP TABLE laporan;--")
        self.assertEqual(self.jalankan_sql("SELECT COUNT(*) FROM laporan")[0][0], 2)

    def test_filter_kategori_status_dan_gabungan(self):
        self.isi_laporan(2, kategori="Fasilitas", judul="Soal fasilitas")
        self.isi_laporan(1, kategori="Kebersihan", judul="Soal kebersihan")
        koneksi = sqlite3.connect(self.db_path)
        koneksi.execute("UPDATE laporan SET status = 'Selesai' WHERE id = 1")
        koneksi.commit()
        koneksi.close()
        self.assertIn("2 laporan ditemukan", self.client.get("/admin/laporan?kategori=Fasilitas").get_data(as_text=True))
        self.assertIn("1 laporan ditemukan", self.client.get("/admin/laporan?kategori=Kebersihan").get_data(as_text=True))
        self.assertIn("1 laporan ditemukan", self.client.get("/admin/laporan?status=Selesai").get_data(as_text=True))
        self.assertIn("2 laporan ditemukan", self.client.get("/admin/laporan?status=Menunggu").get_data(as_text=True))
        self.assertIn("1 laporan ditemukan",
                      self.client.get("/admin/laporan?kategori=Fasilitas&status=Selesai").get_data(as_text=True))
        # Nilai filter palsu diabaikan (dianggap "Semua")
        self.assertIn("3 laporan ditemukan", self.client.get("/admin/laporan?kategori=Palsu&status=Palsu").get_data(as_text=True))

    def test_halaman_pagination(self):
        self.isi_laporan(12)
        halaman1 = self.client.get("/admin/laporan").get_data(as_text=True)
        halaman2 = self.client.get("/admin/laporan?halaman=2").get_data(as_text=True)
        self.assertEqual(halaman1.count('data-nomor="'), 10)
        self.assertEqual(halaman2.count('data-nomor="'), 2)
        self.assertIn("halaman 2 dari 2", halaman2)
        # Nomor halaman ngawur tidak membuat error
        for nilai in ["abc", "0", "-5", "999"]:
            self.assertEqual(self.client.get(f"/admin/laporan?halaman={nilai}").status_code, 200)

    def test_detail_laporan(self):
        self.kirim(deskripsi="Baris satu.\nBaris dua.")
        halaman = self.client.get("/admin/laporan/1").get_data(as_text=True)
        for teks in ["Budi Santoso", "AC kelas XI RPL 1 rusak", "Fasilitas", "Baris satu.", "Baris dua.", "Ubah status"]:
            self.assertIn(teks, halaman)
        self.assertEqual(self.client.get("/admin/laporan/9999").status_code, 404)

    def test_ubah_status(self):
        self.kirim()
        token = self.token("/admin/laporan/1")
        for status in ["Diproses", "Selesai", "Menunggu"]:
            respons = self.client.post("/admin/laporan/1/status", data={"status": status, "csrf_token": token})
            self.assertEqual(respons.status_code, 302)
            self.assertEqual(self.jalankan_sql("SELECT status FROM laporan WHERE id = 1")[0][0], status)
        baris = self.jalankan_sql("SELECT diperbarui_pada, diperbarui_oleh FROM laporan WHERE id = 1")[0]
        self.assertIsNotNone(baris[0])
        self.assertEqual(baris[1], 1)
        self.assertIn("Oleh:", self.client.get("/admin/laporan/1").get_data(as_text=True))

    def test_ubah_status_tidak_valid(self):
        self.kirim()
        token = self.token("/admin/laporan/1")
        self.client.post("/admin/laporan/1/status", data={"status": "Hancur", "csrf_token": token})
        self.assertEqual(self.jalankan_sql("SELECT status FROM laporan WHERE id = 1")[0][0], "Menunggu")
        self.assertEqual(
            self.client.post("/admin/laporan/9999/status", data={"status": "Selesai", "csrf_token": token}).status_code, 404)

    def test_hapus_laporan(self):
        self.isi_laporan(2)
        token = self.token("/admin/laporan")
        respons = self.client.post("/admin/laporan/1/hapus", data={"csrf_token": token})
        self.assertEqual(respons.status_code, 302)
        self.assertEqual(self.jalankan_sql("SELECT COUNT(*) FROM laporan")[0][0], 1)
        self.assertEqual(self.client.post("/admin/laporan/1/hapus", data={"csrf_token": token}).status_code, 404)
        halaman = self.client.get("/admin/laporan").get_data(as_text=True)
        self.assertIn('id="modalHapus"', halaman)  # jendela konfirmasi tersedia

    def test_hapus_admin_mengosongkan_foreign_key(self):
        self.kirim()
        token = self.token("/admin/laporan/1")
        self.client.post("/admin/laporan/1/status", data={"status": "Selesai", "csrf_token": token})
        with self.app.app_context():
            from app.database import get_db
            db = get_db()
            self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            with db:
                db.execute("DELETE FROM admin WHERE id = 1")
            self.assertIsNone(models.ambil_laporan(1)["diperbarui_oleh"])


class TesDatabaseDanAkun(DasarTes):
    def test_tabel_dibuat_otomatis(self):
        tabel = {b[0] for b in self.jalankan_sql("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"admin", "laporan"} <= tabel)

    def test_constraint_database(self):
        koneksi = sqlite3.connect(self.db_path)
        with self.assertRaises(sqlite3.IntegrityError):
            koneksi.execute("INSERT INTO laporan (nama_pelapor, kategori, judul, deskripsi) VALUES ('a','Salah','b','c')")
        koneksi.close()

    def test_simpan_admin(self):
        with self.app.app_context():
            self.assertEqual(simpan_admin("guru.piket", "rahasia-banget-1"), "dibuat")
            self.assertEqual(simpan_admin("guru.piket", "rahasia-baru-22"), "diperbarui")
            with self.assertRaises(ValueError):
                simpan_admin("ab", "rahasia-banget-1")
            with self.assertRaises(ValueError):
                simpan_admin("guru2", "pendek")
            with self.assertRaises(ValueError):
                simpan_admin("nama dengan spasi", "rahasia-banget-1")
        self.assertEqual(self.login("guru.piket", "rahasia-baru-22").status_code, 302)

    def test_database_dibuat_di_folder_baru(self):
        jalur = os.path.join(self.folder.name, "folder", "belum", "ada", "baru.db")
        app = create_app({"SECRET_KEY": "kunci-khusus-pengujian-123456", "DATABASE": jalur})
        self.assertTrue(os.path.exists(jalur))
        self.assertEqual(app.test_client().get("/").status_code, 200)


if __name__ == "__main__":
    unittest.main()
