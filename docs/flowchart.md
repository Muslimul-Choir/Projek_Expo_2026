# Flowchart — Smart To-Do with Reminders

Diagram berikut menggambarkan alur utama aplikasi mulai dari inisialisasi data, navigasi antar layar, pengelolaan tugas (CRUD) dengan validasi, hingga pengecekan pengingat popup secara berkala.

```mermaid
flowchart TD
    Start([Mulai Aplikasi]) --> Load[Muat data/tasks.json atau data contoh]
    Load --> Dash[Tampilkan Halaman Ringkasan]
    Dash --> Timer[Jadwalkan Timer Pengingat 30 detik]

    Dash --> Nav{Pilih Menu Sidebar}
    Nav -->|Ringkasan| Dash
    Nav -->|Daftar tugas| Tasks[Tampilkan Tabel Daftar Tugas]
    Nav -->|Mode fokus| Focus[Tampilkan 1 Tugas Paling Mendesak]

    Tasks --> Action{Pilih Aksi}
    Action -->|Tambah / Ubah| Form[Buka Form Tugas]
    Action -->|Lihat Detail| Detail[Tampilkan Detail Tugas]
    Action -->|Tandai Selesai| Done[Ubah Status ke Completed]
    Action -->|Hapus| Confirm{Konfirmasi Hapus?}

    Form --> Validate{Validasi Input<br/>try / except}
    Validate -->|Gagal| Err[Tampilkan Pesan Error] --> Form
    Validate -->|Valid| Save[Simpan ke TaskManager & JSON]

    Confirm -->|Ya| Save
    Confirm -->|Tidak| Tasks
    Done --> Save
    Focus -->|Klik Tandai Selesai| Done

    Save --> Notify[Perbarui Semua Halaman Otomatis]
    Notify --> Tasks

    Timer --> Check{Ada Tugas Terlambat /<br/>Mendekati Tenggat Baru?}
    Check -->|Ya| Popup[Tampilkan Popup Pengingat]
    Check -->|Tidak| Wait[Tunggu 30 Detik Berikutnya]
    Popup --> Wait
    Wait --> Close{Aplikasi Ditutup?}
    Close -->|Tidak| Timer
    Close -->|Ya| End([Simpan & Keluar])
```
