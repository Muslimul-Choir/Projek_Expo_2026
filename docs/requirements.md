# Requirements Document — Smart To-Do with Reminders

## 1. Informasi Proyek
- **Judul Proyek**: Smart To-Do with Reminders
- **Platform**: Desktop (Windows, Python 3.10+ & Tkinter)
- **Jenis Aplikasi**: Single-user, lokal, tanpa database eksternal

---

## 2. Latar Belakang & Tujuan
Tugas dan aktivitas harian sering terlupa atau terlambat dikerjakan karena catatan tersebar dan tidak ada sistem pengingat terpusat. **Smart To-Do with Reminders** hadir untuk:
1. Menyimpan seluruh tugas, tenggat waktu, dan prioritas dalam satu aplikasi.
2. Mengurutkan tugas secara otomatis berdasarkan urgensi (tenggat terdekat & prioritas tertinggi).
3. Memberikan peringatan popup otomatis sebelum atau saat tenggat terlewat.
4. Membantu pengguna menentukan tugas mana yang harus dikerjakan terlebih dahulu lewat **Mode Fokus**.

---

## 3. Kebutuhan Fungsional (Functional Requirements)

| ID | Kebutuhan |
|---|---|
| **FR-01** | Aplikasi langsung menampilkan halaman **Ringkasan** berisi 4 kartu statistik dan daftar tugas mendatang. |
| **FR-02** | Pengguna dapat menambah, mengubah, melihat detail, menandai selesai, dan menghapus tugas pada halaman **Daftar tugas**. |
| **FR-03** | Setiap tugas memiliki atribut: `task_id`, `title`, `description`, `subject` (kategori), `deadline`, `priority`, `status`, dan `created`. |
| **FR-04** | Tugas diurutkan berdasarkan tenggat terdekat lalu prioritas tertinggi (`High` > `Medium` > `Low`), serta ditandai **Terlambat**, **Hari ini**, atau **Segera**. |
| **FR-05** | Sistem memeriksa tenggat secara berkala setiap 30 detik (`after()`) dan memunculkan **popup pengingat** tanpa mengulang popup yang sama untuk tenggat yang tidak berubah. |
| **FR-06** | Halaman **Mode fokus** merekomendasikan 1 tugas berstatus `Pending` yang paling mendesak beserta tombol **Tandai selesai**. |
| **FR-07** | Seluruh input pengguna divalidasi dan kesalahan ditangani menggunakan `try/except` dengan pesan dialog yang jelas. |
| **FR-08** | Pencarian tugas berdasarkan ID menggunakan fungsi rekursif (`_binary_search`). |
| **FR-09** | Data tugas disimpan otomatis ke `data/tasks.json`; jika file belum ada, aplikasi memuat 5 tugas contoh awal. |

---

## 4. Kebutuhan Teknis & Non-Fungsional

| Aspek | Spesifikasi |
|---|---|
| **OOP** | Minimal 3 class — proyek menerapkan 5 class (`BaseTask`, `Task`, `TaskManager`, `ReminderManager`, `SmartTodoApp`) dengan inheritance dan polymorphism (`describe()`). |
| **Rekursi** | Pencarian biner rekursif pada `TaskManager._binary_search()`. |
| **Error Handling** | `try/except` pada validasi tanggal/jam/ID serta operasi simpan/muat file dan aksi CRUD. |
| **Antarmuka (GUI)** | 3 layar utama dalam satu jendela dengan sidebar navigasi + 1 popup form Tambah/Ubah tugas. |
| **Keandalan** | Aplikasi tidak crash saat input tidak valid atau saat tidak ada baris yang dipilih di tabel. |
| **Sinkronisasi** | Pola observer (`add_listener`) memperbarui seluruh halaman otomatis setiap kali data berubah. |

---

## 5. Kebutuhan Perangkat & Batasan Sistem
- **Perangkat Keras**: PC/Laptop dengan RAM minimal 2 GB dan resolusi layar minimal 1024×600.
- **Perangkat Lunak**: Windows 10/11, Python 3.10+ (Tkinter bawaan, tanpa library pihak ketiga).
- **Batasan**: Penyimpanan lokal berbasis JSON (`data/tasks.json`), pengingat aktif selama aplikasi berjalan, dan untuk penggunaan satu pengguna.
