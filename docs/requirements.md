# Requirements Document — Smart To-Do

## 1. Project Title
Smart To-Do

## 2. Project Overview
Aplikasi desktop (Python + Tkinter) untuk mengatur tugas pribadi, pekerjaan, rumah, dan kegiatan lainnya beserta tenggat, prioritas, dan pengingat. Data dikelola di memori; penyimpanan JSON menjadi fitur tambahan.

## 3. Problem Statement
Tugas dan kegiatan yang tersebar sering terlupakan atau terlambat diselesaikan karena tidak ada daftar dan pengingat terpusat.

## 4. Project Objectives
- Mencatat dan mengelola tugas berdasarkan kategori, tenggat, dan prioritas.
- Menampilkan statistik, kalender, dan tugas terdekat.
- Mengingatkan tugas yang mendekati tenggat atau terlambat.
- Merekomendasikan tugas berikutnya lewat mode fokus.
- Menerapkan OOP, fungsi rekursif, validasi input, dan error handling.

## 5. Functional Requirements
| ID | Kebutuhan |
|----|-----------|
| FR-01 | Ringkasan tampil pertama; tanpa login atau halaman sambutan. |
| FR-02 | Ringkasan memuat statistik, kalender tenggat, tugas terdekat, dan tugas pada tanggal terpilih. |
| FR-03 | Pengguna dapat menambah, mengubah, menghapus, melihat, dan menandai tugas selesai. |
| FR-04 | Data tugas memiliki ID, judul, deskripsi, kategori, tenggat, prioritas, status, dan waktu dibuat. |
| FR-05 | Prioritas tinggi, sedang, dan rendah ditampilkan dengan warna berbeda. |
| FR-06 | Tugas diurutkan menurut tenggat; sistem menandai tugas terlambat dan yang mendekati tenggat. |
| FR-07 | Pengingat diperiksa berkala (`after()`), tanpa popup berulang untuk tugas yang sama. |
| FR-08 | Mode fokus memilih tugas belum selesai dengan tenggat terdekat, lalu prioritas tertinggi. |
| FR-09 | Pengguna dapat mencari dan memfilter berdasarkan status serta prioritas. |
| FR-10 | Input divalidasi dan kesalahan ditampilkan melalui dialog. |
| FR-11 | Pencarian tugas berdasarkan ID memakai fungsi rekursif (binary search). |

## 6. Non-Functional Requirements
- Responsif terhadap ukuran jendela; UI konsisten dan modern.
- Tidak crash saat input salah; kode terstruktur per modul.
- Dashboard diperbarui otomatis lewat pola observer.

## 7. Hardware Requirements
PC/laptop Windows, RAM ≥ 2 GB, layar ≥ 1024×600.

## 8. Software Requirements
Windows 10/11, Python 3.10+ (Tkinter bawaan), tanpa library eksternal.

## 9. User Interface Requirements
Sidebar kiri dan konten kanan. Semua halaman memakai palet konsisten: latar lavender pucat, teks navy keunguan, aksen ungu, kartu putih, serta warna status hijau, merah lembut, dan jingga. Istilah kategori dan tenggat digunakan agar sesuai untuk berbagai jenis tugas.

## 10. System Limitations
- Tanpa database; data hilang jika file `data/tasks.json` dihapus.
- Reminder hanya aktif saat aplikasi terbuka.
- Satu pengguna, lokal saja.
