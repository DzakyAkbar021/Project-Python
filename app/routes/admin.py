"""Halaman admin: login, dashboard, daftar laporan, detail, ubah status, hapus, logout.

Semua halaman (kecuali login) dilindungi dekorator @login_required.
"""
from math import ceil

from flask import (Blueprint, abort, current_app, flash, g, redirect,
                   render_template, request, session, url_for)

from .. import models
from ..constants import KATEGORI, STATUS
from ..security import (HASH_PALSU, PembatasLogin, alamat_aman, cek_password,
                        login_required)

bp = Blueprint("admin", __name__, url_prefix="/admin")

# Dibuat sekali; batasnya diambil dari config saat pertama dipakai.
pembatas_login = PembatasLogin(batas=5, jeda_detik=300)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.admin:
        return redirect(url_for("admin.dashboard"))

    tujuan = request.values.get("next", "")
    status_http = 200

    if request.method == "POST":
        pembatas_login.batas = current_app.config["LOGIN_BATAS_GAGAL"]
        pembatas_login.jeda = current_app.config["LOGIN_JEDA_DETIK"]
        ip = request.remote_addr or "tidak-diketahui"

        if pembatas_login.terkunci(ip):
            flash("Terlalu banyak percobaan login yang gagal. Coba lagi beberapa menit lagi.", "danger")
            status_http = 429
        else:
            username = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")
            akun = models.cari_admin(username)
            # Hash dicek walau akun tidak ada, supaya waktu responsnya sama.
            cocok = cek_password(akun["password_hash"] if akun else HASH_PALSU, password)

            if akun and cocok:
                pembatas_login.reset(ip)
                session.clear()  # sesi baru setelah login
                session["admin_id"] = akun["id"]
                session.permanent = True
                flash(f"Selamat datang, {akun['username']}!", "success")
                return redirect(tujuan if alamat_aman(tujuan) else url_for("admin.dashboard"))

            pembatas_login.catat_gagal(ip)
            flash("Username atau password salah.", "danger")
            status_http = 401

    return render_template("admin/login.html", tujuan=tujuan), status_http


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Anda sudah keluar dari akun admin.", "success")
    return redirect(url_for("admin.login"))


@bp.route("/")
@login_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        stat=models.hitung_statistik(),
        daftar=models.laporan_terbaru(5),
    )


@bp.route("/laporan")
@login_required
def daftar_laporan():
    q = request.args.get("q", "").strip()[:100]
    kategori = request.args.get("kategori", "")
    status = request.args.get("status", "")
    # Filter hanya boleh berisi nilai yang ada di daftar resmi.
    if kategori not in KATEGORI:
        kategori = ""
    if status not in STATUS:
        status = ""
    try:
        halaman = max(1, int(request.args.get("halaman", "1")))
    except ValueError:
        halaman = 1

    per_halaman = current_app.config["LAPORAN_PER_HALAMAN"]
    total = models.hitung_laporan(q, kategori, status)
    total_halaman = max(1, ceil(total / per_halaman))
    halaman = min(halaman, total_halaman)

    return render_template(
        "admin/laporan.html",
        daftar=models.cari_laporan(q, kategori, status, halaman, per_halaman),
        total=total,
        q=q,
        kategori=kategori,
        status=status,
        halaman=halaman,
        total_halaman=total_halaman,
    )


@bp.route("/laporan/<int:laporan_id>")
@login_required
def detail_laporan(laporan_id):
    laporan = models.ambil_laporan(laporan_id)
    if laporan is None:
        abort(404)
    return render_template("admin/detail.html", laporan=laporan)


@bp.route("/laporan/<int:laporan_id>/status", methods=["POST"])
@login_required
def ubah_status(laporan_id):
    status_baru = request.form.get("status", "")
    if status_baru not in STATUS:
        flash("Status tidak valid.", "danger")
    elif models.ubah_status(laporan_id, status_baru, g.admin["id"]):
        flash(f"Status laporan diubah menjadi {status_baru}.", "success")
    else:
        abort(404)
    return redirect(url_for("admin.detail_laporan", laporan_id=laporan_id))


@bp.route("/laporan/<int:laporan_id>/hapus", methods=["POST"])
@login_required
def hapus_laporan(laporan_id):
    if not models.hapus_laporan(laporan_id):
        abort(404)
    flash("Laporan berhasil dihapus.", "success")
    return redirect(url_for("admin.daftar_laporan"))
