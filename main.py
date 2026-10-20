import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# =========================
# DATABASE
# =========================

def koneksi_database():
    return sqlite3.connect("database.db")


def buat_tabel():
    conn = koneksi_database()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nis TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            kelas TEXT NOT NULL,
            jurusan TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# FUNGSI PROGRAM
# =========================

def tampilkan_data():
    # Hapus data lama dari tabel
    for item in tabel.get_children():
        tabel.delete(item)

    conn = koneksi_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM siswa")
    data = cursor.fetchall()

    for siswa in data:
        tabel.insert("", tk.END, values=siswa)

    conn.close()


def tambah_data():
    nis = entry_nis.get()
    nama = entry_nama.get()
    kelas = entry_kelas.get()
    jurusan = entry_jurusan.get()

    if nis == "" or nama == "" or kelas == "" or jurusan == "":
        messagebox.showwarning(
            "Peringatan",
            "Semua data harus diisi!"
        )
        return

    try:
        conn = koneksi_database()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO siswa (nis, nama, kelas, jurusan)
            VALUES (?, ?, ?, ?)
        """, (nis, nama, kelas, jurusan))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Berhasil",
            "Data siswa berhasil ditambahkan!"
        )

        bersihkan_input()
        tampilkan_data()

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error",
            "NIS sudah terdaftar!"
        )


def hapus_data():
    item = tabel.selection()

    if not item:
        messagebox.showwarning(
            "Peringatan",
            "Pilih data yang ingin dihapus!"
        )
        return

    data = tabel.item(item)
    id_siswa = data["values"][0]

    konfirmasi = messagebox.askyesno(
        "Konfirmasi",
        "Apakah kamu yakin ingin menghapus data ini?"
    )

    if konfirmasi:
        conn = koneksi_database()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM siswa WHERE id = ?",
            (id_siswa,)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Berhasil",
            "Data berhasil dihapus!"
        )

        bersihkan_input()
        tampilkan_data()


def pilih_data(event):
    item = tabel.selection()

    if not item:
        return

    data = tabel.item(item)
    nilai = data["values"]

    bersihkan_input()

    entry_nis.insert(0, nilai[1])
    entry_nama.insert(0, nilai[2])
    entry_kelas.insert(0, nilai[3])
    entry_jurusan.insert(0, nilai[4])


def edit_data():
    item = tabel.selection()

    if not item:
        messagebox.showwarning(
            "Peringatan",
            "Pilih data yang ingin diedit!"
        )
        return

    data = tabel.item(item)
    id_siswa = data["values"][0]

    nis = entry_nis.get()
    nama = entry_nama.get()
    kelas = entry_kelas.get()
    jurusan = entry_jurusan.get()

    if nis == "" or nama == "" or kelas == "" or jurusan == "":
        messagebox.showwarning(
            "Peringatan",
            "Semua data harus diisi!"
        )
        return

    try:
        conn = koneksi_database()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE siswa
            SET nis = ?, nama = ?, kelas = ?, jurusan = ?
            WHERE id = ?
        """, (nis, nama, kelas, jurusan, id_siswa))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Berhasil",
            "Data siswa berhasil diperbarui!"
        )

        bersihkan_input()
        tampilkan_data()

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error",
            "NIS sudah digunakan siswa lain!"
        )


def cari_data():
    keyword = entry_cari.get()

    for item in tabel.get_children():
        tabel.delete(item)

    conn = koneksi_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM siswa
        WHERE nis LIKE ?
        OR nama LIKE ?
        OR kelas LIKE ?
        OR jurusan LIKE ?
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    data = cursor.fetchall()

    for siswa in data:
        tabel.insert("", tk.END, values=siswa)

    conn.close()


def bersihkan_input():
    entry_nis.delete(0, tk.END)
    entry_nama.delete(0, tk.END)
    entry_kelas.delete(0, tk.END)
    entry_jurusan.delete(0, tk.END)


def reset_data():
    bersihkan_input()
    entry_cari.delete(0, tk.END)
    tampilkan_data()


# =========================
# MEMBUAT WINDOW
# =========================

buat_tabel()

root = tk.Tk()
root.title("Sistem Pengolahan Data Siswa")
root.geometry("850x600")
root.resizable(False, False)


# =========================
# JUDUL
# =========================

judul = tk.Label(
    root,
    text="SISTEM PENGOLAHAN DATA SISWA",
    font=("Arial", 20, "bold")
)

judul.pack(pady=20)


# =========================
# FORM INPUT
# =========================

frame_form = tk.Frame(root)
frame_form.pack()


tk.Label(
    frame_form,
    text="NIS",
    font=("Arial", 11)
).grid(row=0, column=0, padx=10, pady=7, sticky="w")

entry_nis = tk.Entry(
    frame_form,
    width=30
)
entry_nis.grid(row=0, column=1, padx=10, pady=7)


tk.Label(
    frame_form,
    text="Nama",
    font=("Arial", 11)
).grid(row=1, column=0, padx=10, pady=7, sticky="w")

entry_nama = tk.Entry(
    frame_form,
    width=30
)
entry_nama.grid(row=1, column=1, padx=10, pady=7)


tk.Label(
    frame_form,
    text="Kelas",
    font=("Arial", 11)
).grid(row=2, column=0, padx=10, pady=7, sticky="w")

entry_kelas = tk.Entry(
    frame_form,
    width=30
)
entry_kelas.grid(row=2, column=1, padx=10, pady=7)


tk.Label(
    frame_form,
    text="Jurusan",
    font=("Arial", 11)
).grid(row=3, column=0, padx=10, pady=7, sticky="w")

entry_jurusan = tk.Entry(
    frame_form,
    width=30
)
entry_jurusan.grid(row=3, column=1, padx=10, pady=7)


# =========================
# TOMBOL
# =========================

frame_tombol = tk.Frame(root)
frame_tombol.pack(pady=15)


btn_tambah = tk.Button(
    frame_tombol,
    text="Tambah",
    width=12,
    command=tambah_data
)
btn_tambah.grid(row=0, column=0, padx=5)


btn_edit = tk.Button(
    frame_tombol,
    text="Edit",
    width=12,
    command=edit_data
)
btn_edit.grid(row=0, column=1, padx=5)


btn_hapus = tk.Button(
    frame_tombol,
    text="Hapus",
    width=12,
    command=hapus_data
)
btn_hapus.grid(row=0, column=2, padx=5)


btn_reset = tk.Button(
    frame_tombol,
    text="Reset",
    width=12,
    command=reset_data
)
btn_reset.grid(row=0, column=3, padx=5)


# =========================
# PENCARIAN
# =========================

frame_cari = tk.Frame(root)
frame_cari.pack(pady=5)


tk.Label(
    frame_cari,
    text="Cari:",
    font=("Arial", 11)
).pack(side=tk.LEFT, padx=5)


entry_cari = tk.Entry(
    frame_cari,
    width=35
)
entry_cari.pack(side=tk.LEFT, padx=5)


btn_cari = tk.Button(
    frame_cari,
    text="Cari Data",
    command=cari_data
)
btn_cari.pack(side=tk.LEFT, padx=5)


# =========================
# TABEL DATA
# =========================

frame_tabel = tk.Frame(root)
frame_tabel.pack(pady=15)


kolom = (
    "ID",
    "NIS",
    "Nama",
    "Kelas",
    "Jurusan"
)

tabel = ttk.Treeview(
    frame_tabel,
    columns=kolom,
    show="headings",
    height=10
)

tabel.heading("ID", text="ID")
tabel.heading("NIS", text="NIS")
tabel.heading("Nama", text="Nama")
tabel.heading("Kelas", text="Kelas")
tabel.heading("Jurusan", text="Jurusan")


tabel.column("ID", width=50, anchor="center")
tabel.column("NIS", width=100, anchor="center")
tabel.column("Nama", width=220)
tabel.column("Kelas", width=100, anchor="center")
tabel.column("Jurusan", width=150, anchor="center")


tabel.pack()

# Ketika data tabel diklik
tabel.bind(
    "<ButtonRelease-1>",
    pilih_data
)


# =========================
# MENAMPILKAN DATA AWAL
# =========================

tampilkan_data()


# =========================
# MENJALANKAN PROGRAM
# =========================

root.mainloop()