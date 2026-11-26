# Smart To-Do

Aplikasi desktop untuk mengatur tugas, tenggat waktu, dan prioritas di satu tempat (Python + Tkinter). Tanpa database dan tanpa login — aplikasi langsung membuka halaman Ringkasan.

## Menjalankan
```
python main.py
```
Butuh Python 3.10+ (Tkinter sudah termasuk di installer Windows). Tidak ada library tambahan.
Saat pertama dijalankan, 5 tugas contoh dimuat secara otomatis. Data disimpan di `data/tasks.json`.

## Fitur
- Ringkasan statistik dan daftar tugas mendatang
- Daftar tugas (tambah, ubah, lihat detail, tandai selesai, hapus) dengan validasi input
- Pengurutan otomatis berdasarkan urgensi (tenggat terdekat & prioritas tertinggi) serta penanda tugas terlambat
- Mode fokus untuk menyarankan 1 tugas berikutnya yang paling mendesak
- Pengingat popup otomatis setiap 30 detik untuk tugas yang mendekati tenggat atau terlambat

## Struktur
- `models/task.py` — `BaseTask` (induk) dan `Task` (turunan, override `describe()`).
- `core/task_manager.py` — CRUD, statistik, deteksi tenggat, mode fokus, **pencarian ID rekursif** (`_binary_search`), dan simpan/muat JSON.
- `core/reminder_manager.py` — cek tenggat dan mencegah popup berulang.
- `gui/application.py` — pengendali utama aplikasi, navigasi, dan pengingat berkala.
- `gui/` — pembangun halaman (`dashboard.py`, `task_page.py`, `focus_page.py`, `sidebar.py`, `theme.py`).
- `utils/validators.py` — validasi input form dan ID tugas (`try/except`).
- `docs/` — dokumentasi (`requirements.md`, `flowchart.md`, `wireframe.md`).
- `main.py` — titik masuk aplikasi.
- `data/tasks.json` — penyimpanan tugas lokal.
