"""Titik awal untuk menjalankan website: python run.py"""
import os

from app import create_app

try:
    app = create_app()
except RuntimeError as error:
    # Tampilkan pesan yang mudah dibaca (bukan traceback panjang) lalu berhenti.
    print(f"\n[ERROR] {error}\n")
    raise SystemExit(1)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
