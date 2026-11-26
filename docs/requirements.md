# Requirements Document — Smart To-Do with Reminders

## 1. Project Title
Smart To-Do with Reminders

## 2. Project Overview
Aplikasi desktop (Python + Tkinter) untuk mengatur tugas dan tenggat waktu di satu tempat. Tugas diurutkan berdasarkan urgensi (tenggat terdekat & prioritas tertinggi) dan pengingat popup muncul otomatis saat tenggat mendekati atau terlewat. Data dapat disimpan ke file JSON sebagai fitur tambahan.

## 3. Problem Statement
Tugas dan kegiatan yang tersebar sering terlupakan atau terlambat diselesaikan karena tidak ada daftar dan pengingat terpusat.

## 4. Project Objectives
- Mencatat dan mengelola tugas (tambah, ubah, hapus, selesaikan) dengan tenggat dan prioritas.
- Mengurutkan tugas berdasarkan urgensi serta menandai tugas yang terlambat (`Terlambat` / `Segera`).
- Menampilkan pengingat popup otomatis saat tenggat mendekati atau terlewat.
- Merekomendasikan tugas berikutnya lewat Mode Fokus.
- Menerapkan OOP, fungsi rekursif, validasi input (`try/except`), dan GUI Tkinter multi-layar.

## 5. Functional Requirements
| ID | Kebutuhan |
|----|-----------|
| FR-01 | Halaman Ringkasan tampil pertama kali dengan statistik dan daftar tugas mendatang. |
| FR-02 | Pengguna dapat menambah, mengubah, menghapus, melihat detail, dan menandai tugas selesai. |
| FR-03 | Setiap tugas memiliki tenggat waktu dan prioritas (`High`/`Tinggi`, `Medium`/`Sedang`, `Low`/`Rendah`). |
| FR-04 | Tugas diurutkan menurut urgensi (tenggat terdekat lalu prioritas tertinggi) dan tugas terlambat ditandai khusus. |
| FR-05 | Pengingat popup muncul otomatis secara berkala (`after()`) untuk tugas yang mendekati tenggat atau terlambat, tanpa mengulang popup yang sama. |
| FR-06 | Mode fokus menyarankan satu tugas belum selesai yang paling mendesak untuk dikerjakan berikutnya. |
| FR-07 | Input divalidasi dan kesalahan ditangani dengan `try/except` serta ditampilkan melalui dialog. |
| FR-08 | Pencarian tugas berdasarkan ID memakai fungsi rekursif (binary search). |

## 6. Non-Functional Requirements
- Responsif terhadap ukuran jendela; UI konsisten dan sederhana.
- Tidak crash saat input salah; kode terstruktur per modul.
- Tampilan diperbarui otomatis saat data berubah.

## 7. Hardware & Software Requirements
- PC/laptop Windows, RAM ≥ 2 GB, Python 3.10+ (Tkinter bawaan), tanpa library eksternal.
