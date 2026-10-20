"""Halaman untuk pengunjung umum: beranda dan form pengaduan.

Sengaja TIDAK ada halaman publik yang menampilkan daftar laporan,
sehingga isi laporan hanya bisa dilihat oleh admin.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .. import models
from ..validators import validasi_laporan

bp = Blueprint("public", __name__)


@bp.route("/")
def beranda():
    return render_template("public/index.html")


@bp.route("/lapor", methods=["GET", "POST"])
def form_laporan():
    if request.method == "POST":
        nilai, errors = validasi_laporan(request.form)
        if errors:
            flash("Laporan belum terkirim. Periksa kembali isian yang ditandai merah.", "danger")
            return render_template("public/form.html", nilai=nilai, errors=errors), 400

        _, nomor = models.buat_laporan(**nilai)
        # Nomor disimpan sementara di sesi agar bisa ditampilkan sekali di halaman berhasil.
        session["nomor_laporan"] = nomor
        return redirect(url_for("public.sukses"))

    return render_template("public/form.html", nilai={"jenis": "Pengaduan"}, errors={})


@bp.route("/lapor/berhasil")
def sukses():
    nomor = session.pop("nomor_laporan", None)
    if nomor is None:
        return redirect(url_for("public.form_laporan"))
    return render_template("public/sukses.html", nomor=nomor)
