# AduSekolah — Website Pengaduan dan Saran Sekolah

Website untuk membantu siswa dan warga sekolah menyampaikan **pengaduan dan saran**, serta membantu
**admin** mengelola dan menindaklanjuti laporan. Dibuat untuk kebutuhan Praktik Kerja Lapangan (PKL).

**Teknologi:** Python · Flask · SQLite · HTML/CSS · Bootstrap 5 · Jinja2

---

## 1. Fitur

**Pengguna (tanpa login)**
- Beranda yang menjelaskan fungsi website.
- Form pengaduan/saran: jenis (Pengaduan/Saran), nama pelapor, kategori, judul, deskripsi.
- Kategori: Fasilitas, Kebersihan, Pelayanan, Pembelajaran, Lainnya.
- Validasi: semua kolom wajib diisi, panjang teks dibatasi, kategori harus sesuai daftar.
- Pesan berhasil + **nomor laporan** (contoh `ADU-20261020-0001`).

**Admin (wajib login)**
- Login dengan username dan password, logout.
- Dashboard: kartu statistik (total, menunggu, diproses, selesai) + tabel laporan terbaru.
- Daftar seluruh laporan dengan pencarian (judul / nomor laporan), filter kategori dan status, serta halaman (10 laporan per halaman).
- Detail laporan, ubah status (Menunggu / Diproses / Selesai), hapus laporan dengan jendela konfirmasi.

---

## 2. Struktur Folder

```
adusekolah/
├── run.py                  <- file untuk MENJALANKAN website
├── create_admin.py         <- skrip untuk membuat akun admin pertama
├── config.py               <- pengaturan aplikasi
├── requirements.txt        <- daftar library yang harus diinstal
├── .env.example            <- contoh isi file rahasia (.env)
├── .gitignore              <- daftar file yang tidak boleh masuk GitHub
├── README.md               <- panduan ini
│
├── database/
│   ├── schema.sql          <- rancangan tabel database (admin & laporan)
│   └── adusekolah.db       <- file database (DIBUAT OTOMATIS saat pertama jalan)
│
├── app/
│   ├── __init__.py         <- merakit seluruh aplikasi (create_app)
│   ├── constants.py        <- daftar kategori, jenis, dan status
│   ├── database.py         <- koneksi ke SQLite & pembuatan tabel
│   ├── models.py           <- semua perintah SQL (query)
│   ├── validators.py       <- pemeriksaan isian formulir
│   ├── security.py         <- hash password, login_required, CSRF, batas login
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── public.py       <- halaman pengunjung (beranda, form, berhasil)
│   │   └── admin.py        <- halaman admin (login, dashboard, laporan, dll.)
│   │
│   ├── templates/          <- file HTML (Jinja2)
│   │   ├── base.html       <- kerangka umum: navbar, pesan, footer
│   │   ├── _macros.html    <- potongan HTML yang dipakai ulang (badge status)
│   │   ├── public/         <- index.html, form.html, sukses.html
│   │   ├── admin/          <- login, dashboard, laporan, detail, _tabel_laporan, _modal_hapus
│   │   └── errors/         <- error.html (halaman 404, 400, dll.)
│   │
│   └── static/
│       ├── css/style.css   <- tampilan tambahan (biru-putih-abu)
│       └── js/main.js      <- JavaScript kecil (penghitung huruf, jendela hapus, salin nomor)
│
└── tests/
    └── test_adusekolah.py  <- tes otomatis (opsional dijalankan)
```

> Nama folder **harus persis** seperti di atas (huruf kecil semua). Folder `templates` dan `static` harus berada **di dalam** folder `app`.

---

## 3. Fungsi Setiap File (Penjelasan untuk Pemula)

| File | Fungsinya |
|---|---|
| `run.py` | Pintu masuk. Menjalankan `python run.py` akan menyalakan server website di komputer Anda. |
| `create_admin.py` | Menanyakan username dan password, lalu menyimpan akun admin ke database. Password disimpan sebagai **hash** (kode acak satu arah), bukan teks asli. |
| `config.py` | Menyimpan pengaturan: lokasi database, batas ukuran data, lama sesi login. Membaca `SECRET_KEY` dari file `.env`. |
| `.env` (Anda buat sendiri) | Menyimpan rahasia (SECRET_KEY) di luar kode. Dibuat dengan menyalin `.env.example`. |
| `database/schema.sql` | Berisi perintah SQL pembuat tabel `admin` dan `laporan`. Dijalankan otomatis tiap aplikasi menyala (data lama aman). |
| `app/__init__.py` | "Perakit" aplikasi: memuat konfigurasi, menyiapkan database, mendaftarkan halaman, pengaman CSRF, header keamanan, dan halaman error. |
| `app/constants.py` | Daftar kategori, jenis, dan status di satu tempat agar tidak salah ketik di banyak file. |
| `app/database.py` | Membuka dan menutup koneksi SQLite, mengaktifkan foreign key, membuat tabel dari `schema.sql`. |
| `app/models.py` | Semua perintah SQL (simpan laporan, hitung statistik, cari, ubah status, hapus). Memakai tanda `?` (parameterized SQL) agar aman dari SQL injection. |
| `app/validators.py` | Memeriksa isian form: tidak boleh kosong, batas panjang, kategori harus valid. |
| `app/security.py` | Alat keamanan: membuat/mengecek hash password, dekorator `@login_required`, token CSRF, dan pembatas percobaan login. |
| `app/routes/public.py` | "Rute" halaman publik: `/`, `/lapor`, `/lapor/berhasil`. |
| `app/routes/admin.py` | "Rute" halaman admin: `/admin/login`, `/admin/`, `/admin/laporan`, detail, ubah status, hapus, logout. |
| `app/templates/*.html` | Tampilan HTML. Jinja2 memasukkan data dari Python memakai `{{ ... }}` dan `{% ... %}`. |
| `app/static/css/style.css` | Warna dan gaya tambahan di atas Bootstrap 5. |
| `app/static/js/main.js` | Penghitung karakter, isi jendela konfirmasi hapus, tombol salin nomor. |
| `requirements.txt` | Daftar library (Flask, python-dotenv) untuk diinstal sekali dengan `pip`. |
| `tests/test_adusekolah.py` | Tes otomatis yang memeriksa semua fitur dan keamanan. |

### Daftar route (alamat halaman)

| Alamat | Metode | Fungsi | Perlu login |
|---|---|---|---|
| `/` | GET | Beranda | Tidak |
| `/lapor` | GET, POST | Form dan pengiriman laporan | Tidak |
| `/lapor/berhasil` | GET | Pesan berhasil + nomor laporan | Tidak |
| `/admin/login` | GET, POST | Login admin | Tidak |
| `/admin/logout` | POST | Logout | — |
| `/admin/` | GET | Dashboard | **Ya** |
| `/admin/laporan` | GET | Daftar, cari, filter | **Ya** |
| `/admin/laporan/<id>` | GET | Detail laporan | **Ya** |
| `/admin/laporan/<id>/status` | POST | Ubah status | **Ya** |
| `/admin/laporan/<id>/hapus` | POST | Hapus laporan | **Ya** |

---

## 4. Menjalankan di VS Code (Windows) — Langkah demi Langkah

### Langkah 0 — Pastikan Python sudah terpasang
Buka **Command Prompt**, ketik:
```
python --version
```
Jika muncul `Python 3.10` atau lebih baru, lanjut. Jika tidak: unduh dari <https://www.python.org/downloads/> dan **centang "Add python.exe to PATH"** saat instalasi. (Jika `python` tidak dikenali tetapi sudah terinstal, coba `py --version`, lalu gunakan `py` sebagai pengganti `python` di semua perintah di bawah.)

### Langkah 1 — Buka folder project di VS Code
1. Ekstrak file ZIP project, misalnya ke `C:\Projects\adusekolah`.
2. Di VS Code: **File → Open Folder…** lalu pilih folder `adusekolah` (folder yang berisi `run.py`).
3. Buka terminal: menu **Terminal → New Terminal**. Pastikan alamat di terminal berakhir dengan `adusekolah`.

> ⚠️ Project Flask **tidak dijalankan lewat Live Server / "Open with Live Server"**. Flask dijalankan dari terminal dengan `python run.py`.

### Langkah 2 — Buat virtual environment (ruang library khusus project)
```
python -m venv venv
```
Aktifkan:
```
venv\Scripts\Activate.ps1
```
Jika muncul error *"running scripts is disabled on this system"* (PowerShell), jalankan ini lalu ulangi perintah aktivasi:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
(Alternatif: di **Command Prompt** gunakan `venv\Scripts\activate.bat`.)

Berhasil jika di awal baris terminal muncul **`(venv)`**.
Jika VS Code menanyakan *"We noticed a new environment…"*, klik **Yes**. Atau pilih manual: `Ctrl+Shift+P` → **Python: Select Interpreter** → pilih yang berisi `venv`.

### Langkah 3 — Instal library
```
pip install -r requirements.txt
```

### Langkah 4 — Buat file `.env` berisi SECRET_KEY
1. Salin contohnya:
   ```
   copy .env.example .env
   ```
2. Buat kunci acak:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Buka file `.env` di VS Code, ganti tulisan setelah `SECRET_KEY=` dengan hasil langkah 2 (jangan ada spasi atau tanda kutip). Ubah juga `NAMA_SEKOLAH` sesuai sekolah Anda. Simpan (`Ctrl+S`).

### Langkah 5 — Buat akun admin pertama
```
python create_admin.py
```
Ikuti pertanyaannya (lihat bagian 5). Database `database/adusekolah.db` ikut dibuat otomatis.

### Langkah 6 — Jalankan website
```
python run.py
```
Buka browser ke **<http://127.0.0.1:5000>**. Untuk berhenti, tekan `Ctrl+C` di terminal.

> Website memakai Bootstrap dari internet (CDN), jadi komputer perlu terhubung internet agar tampilannya rapi.

---

## 5. Membuat Akun Admin Pertama

Jalankan di terminal (dengan `(venv)` aktif):
```
python create_admin.py
```
```
Username admin : admin
Password (min. 8 karakter, tidak tampil di layar):
Ulangi password :
Berhasil! Akun admin 'admin' dibuat.
```
- Saat mengetik password, **layar tidak menampilkan apa pun** — itu normal, tetap ketik lalu tekan Enter.
- Username: 3–30 karakter (huruf, angka, `.`, `_`, `-`), otomatis diubah ke huruf kecil. Password: minimal 8 karakter.
- Password tidak pernah disimpan asli; database hanya menyimpan hash (`pbkdf2:sha256:...`).
- **Lupa password?** Jalankan lagi `python create_admin.py`, ketik username yang sama, jawab `y` untuk mengganti passwordnya.
- Ingin admin tambahan? Jalankan lagi dengan username berbeda.

Login di <http://127.0.0.1:5000/admin/login>.

---

## 6. Cara Menguji Seluruh Fitur

### A. Uji manual (di browser)

| # | Langkah | Hasil yang benar |
|---|---|---|
| 1 | Buka `/` | Beranda tampil rapi, ada tombol **Buat Laporan**. |
| 2 | Buka `/lapor`, klik **Kirim** dengan kolom kosong | Browser meminta kolom diisi. |
| 3 | Isi nama/judul/deskripsi dengan **spasi saja**, kirim | Muncul pesan merah "wajib diisi" dan isian lain tidak hilang. |
| 4 | Isi semua kolom dengan benar, kirim | Halaman "Laporan berhasil dikirim" + nomor `ADU-…`. Catat nomornya. |
| 5 | Muat ulang (F5) halaman berhasil | Diarahkan kembali ke form (nomor hanya tampil sekali, demi privasi). |
| 6 | Kirim 2–3 laporan lagi dengan kategori berbeda | Nomor bertambah urut (`…-0002`, `…-0003`). |
| 7 | Buka `/admin/` **sebelum login** | Diarahkan ke halaman login. |
| 8 | Login dengan password salah | Pesan "Username atau password salah." |
| 9 | Login dengan benar | Masuk ke dashboard; kartu statistik menunjukkan jumlah yang sesuai. |
| 10 | Klik menu **Laporan** | Semua laporan tampil dalam tabel. |
| 11 | Cari sebagian judul, lalu cari sebagian nomor laporan | Hanya laporan yang cocok yang tampil. |
| 12 | Pilih filter Kategori, lalu Status, lalu keduanya | Tabel menyesuaikan; tombol **Reset** menghapus filter. |
| 13 | Klik nomor laporan / ikon mata | Halaman detail menampilkan seluruh isi laporan. |
| 14 | Ubah status ke **Diproses**, simpan | Muncul pesan sukses; di dashboard angka *Menunggu* turun dan *Diproses* naik. |
| 15 | Ubah ke **Selesai** | Angka *Selesai* bertambah. |
| 16 | Klik **Hapus** | Muncul jendela konfirmasi. **Batal** = tidak terhapus; **Ya, hapus** = terhapus. |
| 17 | Klik **Keluar** | Kembali ke login; membuka `/admin/` lagi meminta login. |
| 18 | Perkecil jendela browser / buka lewat ponsel (alamat IP komputer harus diizinkan; atau pakai mode responsif `F12`) | Navbar menjadi tombol menu, tabel bisa digeser. |
| 19 | Kirim laporan berjudul `<b>tes</b>` lalu lihat di admin | Tampil sebagai teks `<b>tes</b>`, bukan huruf tebal (aman dari XSS). |

### B. Uji otomatis

```
python -m unittest discover -s tests -t . -v
```
Ada 45 tes yang memeriksa validasi, login, proteksi halaman admin, CSRF, SQL injection, XSS, pencarian, filter, halaman, ubah status, hapus, dan pembuatan akun. Tes memakai database sementara sehingga **data Anda tidak tersentuh**. Hasil akhir yang benar: `OK` (butuh sekitar 30 detik karena proses hash password sengaja dibuat berat).

---

## 7. Keamanan yang Diterapkan

| Kebutuhan | Cara penerapan |
|---|---|
| Halaman admin dilindungi login | Dekorator `@login_required` pada semua halaman dan aksi admin. |
| Password tidak disimpan polos | Hash PBKDF2-SHA256 (600.000 putaran) + salt acak. |
| Validasi data formulir | `app/validators.py` (di server, bukan hanya di browser) + `CHECK` di database. |
| Cegah SQL injection | Semua query memakai parameter `?` (`app/models.py`). Pencarian juga meng-escape `%` dan `_`. |
| Perubahan status & hapus butuh admin | Rute POST memakai `@login_required` **dan** token CSRF. |
| Secret key lewat environment variable | Dibaca dari `.env` / environment; aplikasi menolak jalan jika belum diisi. |
| Data pengaduan tidak tampil ke publik | Tidak ada halaman publik berisi daftar laporan; halaman berhasil hanya menampilkan nomor. |
| Tambahan | Token CSRF di semua form, escape otomatis Jinja2 (anti-XSS), batas 5 kali login gagal per 5 menit, cookie sesi `HttpOnly` + `SameSite=Lax`, sesi berakhir 2 jam, header keamanan, `Cache-Control: no-store`, `next=` login hanya ke alamat internal. |

Catatan jujur: ini sudah cukup baik untuk proyek PKL dan jaringan sekolah, tetapi belum mencakup hal seperti pembatasan kirim laporan berulang (anti-spam/CAPTCHA) atau HTTPS otomatis. Lihat bagian 10.

---

## 8. Solusi Error Umum

**`ModuleNotFoundError: No module named 'flask'` (atau `dotenv`)**
Library belum terpasang, atau virtual environment tidak aktif. Pastikan terminal menampilkan `(venv)`, lalu jalankan `pip install -r requirements.txt`. Pastikan juga interpreter VS Code memilih `venv` (`Ctrl+Shift+P` → *Python: Select Interpreter*). Jangan menjalankan lewat tombol ▶ jika interpreternya salah; gunakan terminal.

**`ModuleNotFoundError: No module named 'app'` atau `'config'`**
Perintah dijalankan dari folder yang salah. Terminal harus berada di folder yang berisi `run.py` (ketik `dir` untuk melihat isinya), lalu jalankan ulang.

**`jinja2.exceptions.TemplateNotFound: ...html`**
Flask tidak menemukan file HTML. Periksa: (1) folder `templates` ada **di dalam** `app/`, bukan di luar; (2) nama folder dan file persis sama, huruf kecil semua (`public/index.html`, `admin/dashboard.html`); (3) ekstensi benar `.html`, bukan `.html.txt` (aktifkan tampilan ekstensi file di Windows); (4) Anda menjalankan `python run.py` dari folder utama.

**Database tidak ditemukan / `sqlite3.OperationalError: unable to open database file`**
Folder `database` dan file `schema.sql` harus ada di folder utama (file `.db` dibuat otomatis). Jalankan dari folder utama project. Jika project berada di folder yang dikunci (misalnya sinkronisasi OneDrive atau folder sistem), pindahkan ke `C:\Projects\adusekolah`. Anda juga bisa mengatur `DATABASE_PATH=C:\data\adusekolah.db` di `.env`.

**`RuntimeError: SECRET_KEY belum diatur dengan benar`**
File `.env` belum dibuat atau `SECRET_KEY` masih berisi contoh. Ulangi Langkah 4.

**`sqlite3.OperationalError: no such table: laporan`**
Database lama atau rusak. Hentikan server, hapus file `database/adusekolah.db`, jalankan `python create_admin.py` lagi (tabel dibuat ulang). *Catatan: semua data laporan ikut hilang.*

**`Address already in use` / port 5000 dipakai**
Ubah `PORT=5001` di `.env`, lalu buka `http://127.0.0.1:5001`. Atau tutup program lain yang memakai port tersebut.

**Tampilan berantakan (tanpa warna/gaya)**
Komputer tidak terhubung internet sehingga Bootstrap CDN tidak termuat. Sambungkan internet lalu muat ulang dengan `Ctrl+F5`. Tombol Hapus juga baru berfungsi setelah Bootstrap termuat.

**Form menampilkan "Permintaan tidak valid" (400)**
Sesi formulir kedaluwarsa atau cookie diblokir. Muat ulang halaman form lalu kirim lagi.

**`python` tidak dikenali di terminal**
Python belum masuk PATH. Instal ulang dengan mencentang *Add python.exe to PATH*, atau gunakan `py` sebagai pengganti `python`.

**Perubahan kode tidak terlihat**
Pastikan `FLASK_DEBUG=1` di `.env` (muat ulang otomatis) atau hentikan (`Ctrl+C`) lalu jalankan ulang `python run.py`. Tekan `Ctrl+F5` di browser untuk CSS/JS.

---

## 9. Deployment (Opsional — Lakukan Setelah Berjalan Baik di Lokal)

Pastikan semua uji di bagian 6 sudah lulus di komputer Anda. Lalu, pada server sungguhan:

1. Atur environment variable: `SECRET_KEY` (baru, acak, rahasia), `FLASK_DEBUG=0`, dan `SESSION_COOKIE_SECURE=1` **hanya jika memakai HTTPS**.
2. Jangan jalankan `python run.py` di server publik. Pakai server produksi:
   - Linux: `pip install gunicorn` lalu `gunicorn run:app`
   - Windows: `pip install waitress` lalu `waitress-serve --listen=0.0.0.0:8000 run:app`
3. Pasang HTTPS (misalnya lewat reverse proxy seperti Nginx atau layanan hosting yang menyediakannya).
4. Jalankan `python create_admin.py` di server untuk membuat akun admin di sana.
5. File database `database/adusekolah.db` harus berada di penyimpanan yang **permanen** (hosting dengan disk sementara akan menghapus data). Lakukan cadangan (backup) berkala.
6. Untuk jaringan lokal sekolah (intranet): ubah `host="127.0.0.1"` di `run.py` menjadi `host="0.0.0.0"` dan izinkan port di firewall. Gunakan server produksi seperti di atas, bukan mode debug.

---

## 10. Ide Pengembangan

- Cek status laporan oleh pelapor memakai nomor + kode rahasia (perlu desain privasi tambahan).
- Catatan/tanggapan admin pada tiap laporan.
- Ekspor laporan ke Excel/PDF.
- Grafik laporan per kategori di dashboard.
- Anti-spam (CAPTCHA atau batas kirim per perangkat).
- Banyak peran admin (kepala sekolah, guru piket).

Selamat mengerjakan PKL! 🎓
