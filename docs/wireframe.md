# Wireframe — Smart To-Do with Reminders

## Tema & Tata Letak Umum
- **Sidebar Kiri** (`#17365D` Navy): Logo aplikasi dan menu navigasi (`Ringkasan`, `Daftar tugas`, `Mode fokus`) dengan indikator aktif biru (`#2563EB`).
- **Area Konten Kanan** (`#F4F8FF` Biru Pucat): Kartu putih (`#FFFFFF`) dengan garis tepi lembut (`#DCE7F5`).
- **Warna Status & Prioritas**: Hijau (`#39866A` / Rendah), Jingga (`#C98547` / Sedang / Segera), Merah (`#C85D68` / Tinggi / Terlambat).

---

## 1. Halaman Ringkasan (`dashboard.py`)
```text
+---------------+------------------------------------------------------+
| Smart To-Do   | Ringkasan aktivitasmu                                |
| Rencana,      | Pantau tenggat dan progres tugasmu di satu tempat    |
| lebih teratur |                                                      |
| ------------- | +------------+ +------------+ +-----------+ +------+ |
| MENU          | | 1          | | 2          | | 0         | | 5    | |
| > Ringkasan   | | Hari ini   | | Segera     | | Selesai   | | Semua| |
|   Daftar tugas| +------------+ +------------+ +-----------+ +------+ |
|   Mode fokus  |                                                      |
|               | +--------------------------------------------------+ |
|               | | Tugas mendatang                                  | |
|               | | Tugas            | Kategori       | Tenggat      | |
|               | | -----------------|----------------|------------- | |
|               | | Kirim proposal   | Pekerjaan      | 2026-11-...  | |
|               | | Belanja kebutuhan| Pribadi        | 2026-11-...  | |
|               | +--------------------------------------------------+ |
| Semua tugas,  |                                                      |
| satu tempat.  |                                                      |
+---------------+------------------------------------------------------+
```

---

## 2. Halaman Daftar Tugas (`task_page.py`)
```text
+---------------+------------------------------------------------------+
| SIDEBAR       | Daftar tugas                                         |
|               | Atur pekerjaan, kegiatan, dan hal penting lainnya    |
| > Daftar tugas|                                                      |
|               | +--------------------------------------------------+ |
|               | | Semua tugas                              5 tugas | |
|               | | Judul  | Kategori | Tenggat | Prioritas | Status | |
|               | | -------|----------|---------|-----------|--------| |
|               | | ...    | ...      | ...     | Tinggi    | Belum  | |
|               | +--------------------------------------------------+ |
|               | [+ Tambah] [Ubah] [Lihat] [Selesai] [Hapus]          |
|               |                 Klik dua kali untuk melihat detail.  |
+---------------+------------------------------------------------------+
```

---

## 3. Popup Form Tambah / Ubah Tugas (`task_page.py`)
```text
+--------------------------------------------------+
| Tambah / Ubah tugas                              |
+--------------------------------------------------+
| Judul *              [________________________]  |
| Deskripsi            [________________________]  |
|                      [________________________]  |
| Kategori             [________________________]  |
| Tanggal (YYYY-MM-DD) [2026-11-26              ]  |
| Jam (HH:MM) *        [23:59                   ]  |
| Prioritas *          [Sedang                 v]  |
|                                                  |
|                      [Simpan]  [Batal]           |
+--------------------------------------------------+
```

---

## 4. Halaman Mode Fokus (`focus_page.py`)
```text
+---------------+------------------------------------------------------+
| SIDEBAR       | Mode fokus                                           |
|               | Selesaikan satu hal penting dalam satu waktu         |
| > Mode fokus  |                                                      |
|               | +--------------------------------------------------+ |
|               | | BERIKUTNYA                                       | |
|               | | Kirim proposal                                   | |
|               | | Kategori      : Pekerjaan                        | |
|               | | Tenggat waktu : 2026-11-26 20:00                 | |
|               | | Deskripsi     : Periksa lampiran sebelum dikirim | |
|               | |                                                  | |
|               | | Prioritas: Tinggi                                | |
|               | | 5 jam 0 menit lagi                               | |
|               | |                                                  | |
|               | | [Tandai selesai]                                 | |
|               | +--------------------------------------------------+ |
|               | Urutan: belum selesai, tenggat terdekat, prioritas.  |
+---------------+------------------------------------------------------+
```

---

## 5. Popup Pengingat Otomatis (`application.py`)
```text
+--------------------------------------------------+
| (!) Pengingat tenggat                            |
+--------------------------------------------------+
| TUGAS TERLAMBAT:                                 |
|   - Tugas A (Kategori) - Terlambat 1 jam 20 mnt  |
|                                                  |
| TENGGAT WAKTU MENDEKAT:                          |
|   - Kirim proposal (Pekerjaan) - 2026-11-26 ...  |
|                                                  |
|                       [ OK ]                     |
+--------------------------------------------------+
```
