# Smart To-Do with Reminders

> Aplikasi desktop manajemen tugas berbasis **Python & Tkinter** yang membantu mengatur tenggat waktu, prioritas, mode fokus, dan pengingat otomatis dalam satu tempat.

Tanpa database dan tanpa login — saat dibuka, aplikasi langsung menampilkan halaman **Ringkasan** dengan statistik tugas dan jadwal mendatang.

---

## Fitur Utama

- **Ringkasan Aktivitas**: Menampilkan 4 kartu statistik (*Hari ini*, *Segera*, *Selesai*, *Semua tugas*) serta daftar 5 tugas terdekat.
- **Kelola Tugas (CRUD)**: Tambah, ubah, lihat detail, tandai selesai, dan hapus tugas lengkap dengan deskripsi, kategori, tenggat (`YYYY-MM-DD HH:MM`), serta prioritas (*Tinggi*, *Sedang*, *Rendah*).
- **Pengurutan Urgensi & Penanda Tenggat**: Daftar tugas otomatis diurutkan berdasarkan tenggat terdekat lalu prioritas tertinggi, dengan penanda visual **Terlambat**, **Hari ini**, dan **Segera**.
- **Mode Fokus**: Merekomendasikan **1 tugas belum selesai** yang paling mendesak agar pengguna bisa fokus menyelesaikannya satu per satu.
- **Popup Pengingat Otomatis**: Memeriksa tenggat setiap **30 detik** menggunakan `after()` dan menampilkan popup peringatan tanpa mengulang notifikasi yang sama untuk tenggat yang belum berubah.
- **Penyimpanan Lokal (JSON)**: Data tersimpan otomatis di `data/tasks.json` (saat pertama kali dijalankan, 5 tugas contoh dimuat otomatis).

---

## Kriteria Teknis yang Terpenuhi

| Kriteria | Implementasi di Proyek |
|---|---|
| **Minimal 3 Class** | Memiliki **5 class**: `BaseTask`, `Task`, `TaskManager`, `ReminderManager`, `SmartTodoApp` |
| **Inheritance & Polymorphism** | `Task(BaseTask)` mewarisi `BaseTask` & menimpa `describe()`; `SmartTodoApp(tk.Tk)` mewarisi `tk.Tk` |
| **Fungsi Rekursif** | `TaskManager._binary_search()` mencari tugas berdasarkan `task_id` secara rekursif |
| **`try/except` Input Pengguna** | Validasi tanggal, jam, ID, dan aksi form/tabel di `utils/validators.py` & `gui/application.py` |
| **Tkinter GUI (2+ Layar)** | 3 halaman utama (`Ringkasan`, `Daftar tugas`, `Mode fokus`) + popup form Tambah/Ubah tugas |

---

## Struktur Proyek

```text
Projek_Expo_2026/
├── main.py                  # Titik masuk aplikasi
├── models/
│   └── task.py              # Class BaseTask & Task (OOP, property, status tenggat)
├── core/
│   ├── task_manager.py      # Class TaskManager (CRUD, binary search rekursif, JSON)
│   └── reminder_manager.py  # Class ReminderManager (deteksi pengingat & anti-spam)
├── utils/
│   └── validators.py        # Validasi input pengguna & ValidationError
├── gui/
│   ├── application.py       # Class SmartTodoApp (controller, navigasi, timer popup)
│   ├── sidebar.py           # Sidebar navigasi & ikon Canvas
│   ├── dashboard.py         # Halaman Ringkasan
│   ├── task_page.py         # Halaman Daftar Tugas & popup form Tambah/Ubah
│   ├── focus_page.py        # Halaman Mode Fokus
│   └── theme.py             # Palet warna, styling ttk, & helper widget
├── docs/
│   ├── requirements.md      # Dokumen kebutuhan sistem
│   ├── flowchart.md         # Diagram alur fitur utama
│   └── wireframe.md         # Rancangan tampilan tiap layar
└── data/
    └── tasks.json           # Penyimpanan data tugas lokal
```

---

## Pembagian Tugas Kelompok (5 Anggota)

| Anggota | Class Utama | File Pendukung | Fokus Tanggung Jawab |
|---|---|---|---|
| **Anggota 1** | `BaseTask` | `utils/validators.py`, `docs/requirements.md` | Atribut dasar, encapsulation `@property`, validasi input |
| **Anggota 2** | `Task` | `data/tasks.json` | Inheritance, polymorphism `describe()`, status tenggat, JSON |
| **Anggota 3** | `TaskManager` | `docs/flowchart.md` | CRUD, `_binary_search` rekursif, pengurutan, Mode Fokus |
| **Anggota 4** | `ReminderManager` | `gui/dashboard.py`, `gui/focus_page.py`, `docs/wireframe.md` | Logika pengingat anti-duplikat, tampilan Ringkasan & Fokus |
| **Anggota 5** | `SmartTodoApp` | `main.py`, `gui/theme.py`, `gui/sidebar.py`, `gui/task_page.py` | Pengendali utama GUI, navigasi, popup pengingat, `try/except` |

---

## Cara Menjalankan

1. Pastikan **Python 3.10+** sudah terpasang (Tkinter sudah termasuk bawaan Python di Windows).
2. Jalankan perintah berikut di terminal pada folder proyek:
   ```bash
   python main.py
   ```

---

## Dokumentasi
- [Requirements Document](docs/requirements.md)
- [Flowchart Fitur Utama](docs/flowchart.md)
- [Wireframe Antarmuka](docs/wireframe.md)
