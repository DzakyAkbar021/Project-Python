// JavaScript kecil untuk AduSekolah.
document.addEventListener('DOMContentLoaded', function () {

  // 1) Penghitung karakter pada form laporan.
  document.querySelectorAll('[data-counter-for]').forEach(function (penghitung) {
    var kolom = document.getElementById(penghitung.dataset.counterFor);
    var batas = penghitung.dataset.max;
    if (!kolom) return;
    function perbarui() {
      penghitung.textContent = kolom.value.length + '/' + batas;
    }
    kolom.addEventListener('input', perbarui);
    perbarui();
  });

  // 2) Jendela konfirmasi hapus: isi sesuai tombol Hapus yang diklik.
  var modalHapus = document.getElementById('modalHapus');
  if (modalHapus) {
    modalHapus.addEventListener('show.bs.modal', function (event) {
      var tombol = event.relatedTarget;
      if (!tombol) return;
      modalHapus.querySelector('form').action = tombol.dataset.action;
      modalHapus.querySelector('[data-isi="nomor"]').textContent = tombol.dataset.nomor;
      modalHapus.querySelector('[data-isi="judul"]').textContent = tombol.dataset.judul;
    });
  }

  // 3) Tombol "Salin nomor" di halaman laporan berhasil.
  var tombolSalin = document.getElementById('tombolSalin');
  if (tombolSalin) {
    tombolSalin.addEventListener('click', function () {
      var teks = tombolSalin.dataset.salin;
      var label = tombolSalin.querySelector('span');
      function tandai() {
        label.textContent = 'Tersalin!';
        setTimeout(function () { label.textContent = 'Salin nomor'; }, 2000);
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(teks).then(tandai);
      } else {
        // Cadangan untuk browser lama / alamat non-HTTPS.
        var sementara = document.createElement('textarea');
        sementara.value = teks;
        document.body.appendChild(sementara);
        sementara.select();
        document.execCommand('copy');
        document.body.removeChild(sementara);
        tandai();
      }
    });
  }
});
