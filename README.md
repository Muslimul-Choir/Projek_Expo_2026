# Smart To-Do

Aplikasi desktop untuk mengatur tugas pribadi, pekerjaan, rumah, dan kegiatan lainnya (Python + Tkinter). Tanpa database dan tanpa login — aplikasi langsung membuka ringkasan.

## Menjalankan
```
cd smart_todo
python main.py
```
Butuh Python 3.10+ (Tkinter sudah termasuk di installer Windows). Tidak ada library tambahan.
Saat pertama dijalankan, 5 tugas contoh dimuat. Data disimpan otomatis di `data/tasks.json`. Jika ditemukan `tasks.json` lama di folder utama, isinya disalin ke lokasi baru dan file lama dibiarkan sebagai cadangan.

## Fitur
Ringkasan statistik dan kalender tenggat, daftar tugas dengan kategori serta pencarian/filter, tambah dan ubah tugas dengan validasi, mode fokus, dan pengingat otomatis tiap 30 detik.

## Struktur
- `models/task.py` — `BaseTask` (parent) dan `Task` (child, override `describe()`).
- `core/task_manager.py` — CRUD, statistik, tenggat, mode fokus, **pencarian ID rekursif** (`_binary_search`).
- `core/reminder_manager.py` — cek tenggat dan mencegah popup berulang.
- `gui/application.py` — pengendali aplikasi, navigasi, dan pengingat berkala.
- `gui/` — pembangun halaman ringkasan, daftar tugas, fokus, pengingat, serta tema; halaman bukan class.
- `utils/validators.py` — validasi input.
- `main.py` — titik masuk aplikasi.
- `data/tasks.json` — penyimpanan tugas lokal.

Aplikasi memiliki tepat **5 class inti**: `BaseTask`, `Task`, `TaskManager`,
`ReminderManager`, dan `SmartTodoApp`. State internal memakai atribut berawalan
`_` dan diakses lewat property bila diperlukan; tidak ada class tambahan untuk
halaman GUI. Class yang hanya dipakai oleh test tidak termasuk hitungan class aplikasi.

## Pembagian Role
| Role | File utama |
|------|-----------|
| 01 Core Logic | `core/task_manager.py` |
| 02 OOP Design | `models/task.py`, `core/reminder_manager.py` |
| 03 GUI | `gui/*`, `main.py` |
| 04 Testing | `utils/validators.py`, `tests/` |
| 05 Design & Docs | `docs/*`, `README.md` |

## Pengujian
```
python -m unittest discover -s tests -p "test_core.py" -v
python -m unittest tests.test_gui_smoke -v
```
Test GUI membuka jendela nyata dan menekan tombol lewat kode (messagebox di-mock).
