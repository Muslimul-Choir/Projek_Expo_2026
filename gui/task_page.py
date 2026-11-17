"""Widget builders untuk daftar tugas dan form Add/Edit."""
import calendar
import tkinter as tk
from datetime import date
from tkinter import ttk

from gui.theme import (
    BG, WHITE, TEXT, MUTED, FONT, NAVY, BLUE, BLUE_HOVER, HOVER_LIGHT,
    PRIORITY_COLORS, PRIORITY_LABELS,
    make_card, page_header, make_tree,
)
from models.task import PRIORITIES

MONTHS = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)


def _open_date_picker(parent, app):
    if app._date_picker_window is not None and app._date_picker_window.winfo_exists():
        app._date_picker_window.lift()
        return

    selected_date = app.date_value or date.today()
    month = [selected_date.year, selected_date.month]
    popup = tk.Toplevel(parent)
    app._date_picker_window = popup
    popup.title("Pilih tanggal")
    popup.resizable(False, False)
    popup.transient(parent)
    popup.configure(bg=BG)

    def close():
        app._date_picker_window = None
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", close)
    content = tk.Frame(popup, bg=WHITE, padx=14, pady=14)
    content.pack(fill="both", expand=True, padx=1, pady=1)
    header = tk.Frame(content, bg=WHITE)
    header.pack(fill="x", pady=(0, 10))
    header.columnconfigure(1, weight=1)
    month_label = tk.Label(
        header, text="", bg=WHITE, fg=NAVY, font=(FONT, 11, "bold"))
    month_label.grid(row=0, column=1, sticky="ew")

    def change_month(offset):
        month_index = month[1] - 1 + offset
        month[0] += month_index // 12
        month[1] = month_index % 12 + 1
        render_month()

    ttk.Button(
        header, text="‹", width=3, style="Ghost.TButton",
        command=lambda: change_month(-1),
    ).grid(row=0, column=0, sticky="w")
    ttk.Button(
        header, text="›", width=3, style="Ghost.TButton",
        command=lambda: change_month(1),
    ).grid(row=0, column=2, sticky="e")

    grid = tk.Frame(content, bg=WHITE)
    grid.pack(fill="both", expand=True)
    for column, weekday in enumerate(("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")):
        grid.columnconfigure(column, weight=1, uniform="weekday")
        tk.Label(grid, text=weekday, bg=WHITE, fg=MUTED,
                 font=(FONT, 8, "bold")).grid(
                     row=0, column=column, sticky="ew", pady=(0, 5))

    def choose_day(day):
        app.date_value = date(month[0], month[1], day)
        app.date_var.set(app.date_value.isoformat())
        close()

    def render_month():
        month_label.config(text=f"{MONTHS[month[1] - 1]} {month[0]}")
        for widget in grid.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
        for row, week in enumerate(
                calendar.Calendar(firstweekday=calendar.MONDAY).monthdayscalendar(
                    month[0], month[1]), start=1):
            for column, day in enumerate(week):
                if not day:
                    continue
                day_date = date(month[0], month[1], day)
                is_selected = day_date == selected_date
                tk.Button(
                    grid, text=str(day), font=(FONT, 9), width=4, relief="flat",
                    bd=0, bg=BLUE if is_selected else WHITE,
                    fg=WHITE if is_selected else NAVY,
                    activebackground=BLUE_HOVER if is_selected else HOVER_LIGHT,
                    activeforeground=WHITE if is_selected else NAVY,
                    command=lambda value=day: choose_day(value),
                ).grid(row=row, column=column, sticky="nsew", padx=1, pady=1)

    render_month()
    popup.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - popup.winfo_width()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - popup.winfo_height()) // 2
    popup.geometry(f"+{max(x, 0)}+{max(y, 0)}")


def build_task_page(parent, app):
    page = tk.Frame(parent, bg=BG)
    page.columnconfigure(0, weight=1)
    page.rowconfigure(2, weight=1)
    page_header(page, "Daftar tugas", "Atur pekerjaan, kegiatan, dan hal penting lainnya").grid(
        row=0, column=0, sticky="w", pady=(0, 16))

    bar = make_card(page)
    bar.grid(row=1, column=0, sticky="ew")
    inner = tk.Frame(bar, bg=WHITE)
    inner.pack(fill="x", padx=14, pady=12)
    inner.columnconfigure(0, weight=1)

    app.search_var = tk.StringVar()
    app.status_var = tk.StringVar(value="Semua")
    app.prio_var = tk.StringVar(value="Semua")
    for column in range(3):
        inner.columnconfigure(column, weight=1 if column == 0 else 0)

    fields = (
        ("CARI TUGAS", ttk.Entry(inner, textvariable=app.search_var, width=28)),
        ("STATUS", ttk.Combobox(
            inner, textvariable=app.status_var,
            values=["Semua", "Belum selesai", "Selesai"],
            state="readonly", width=14,
        )),
        ("PRIORITAS", ttk.Combobox(
            inner, textvariable=app.prio_var,
            values=["Semua", *(PRIORITY_LABELS[p] for p in PRIORITIES)],
            state="readonly", width=13,
        )),
    )
    for column, (label, widget) in enumerate(fields):
        tk.Label(inner, text=label, bg=WHITE, fg=MUTED,
                 font=(FONT, 8, "bold")).grid(
                     row=0, column=column, sticky="w", pady=(0, 5),
                     padx=(0, 12) if column < 2 else 0)
        widget.grid(row=1, column=column, sticky="ew" if column == 0 else "w",
                    padx=(0, 12) if column < 2 else 0)
    for variable in (app.search_var, app.status_var, app.prio_var):
        variable.trace_add("write", lambda *_args: app._refresh_tasks())

    card = make_card(page)
    card.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
    card.columnconfigure(0, weight=1)
    card.rowconfigure(1, weight=1)
    tk.Label(card, text="Semua tugas", bg=WHITE, fg=NAVY,
             font=(FONT, 12, "bold")).grid(
                 row=0, column=0, sticky="w", padx=14, pady=(12, 0))
    app.task_count_lbl = tk.Label(card, text="", bg=WHITE, fg=MUTED,
                                  font=(FONT, 9))
    app.task_count_lbl.grid(row=0, column=1, sticky="e", padx=14, pady=(12, 0))
    columns = [
        ("title", "Judul"), ("subject", "Kategori"),
        ("deadline", "Tenggat"), ("prio", "Prioritas"), ("status", "Status"),
        ("alert", "Penanda"),
    ]
    frame, app.task_tree = make_tree(
        card, columns, [205, 115, 130, 85, 115, 90], height=10)
    frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    app.task_tree.configure(style="TaskList.Treeview")
    for priority, color in PRIORITY_COLORS.items():
        app.task_tree.tag_configure(f"p_{priority}", foreground=color)
    app.task_tree.bind("<Double-1>", lambda _event: app.view_selected_task())

    buttons = tk.Frame(page, bg=BG)
    buttons.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    tk.Label(buttons, text="Klik dua kali tugas untuk melihat detail.",
             bg=BG, fg=MUTED, font=(FONT, 9)).pack(side="right", pady=6)
    actions = (
        ("+ Tambah", "Primary", app.add_task),
        ("Ubah", "Navy", app.edit_selected_task),
        ("Lihat", "Ghost", app.view_selected_task),
        ("Selesai", "Success", app.complete_selected_task),
        ("Hapus", "Danger", app.delete_selected_task),
    )
    for text, style, command in actions:
        ttk.Button(buttons, text=text, style=f"{style}.TButton", command=command).pack(
            side="left", padx=(0, 8))
    return page


def build_task_form_window(parent, app):
    window = tk.Toplevel(parent)
    window.title("Tambah tugas")
    window.geometry("540x500")
    window.minsize(500, 460)
    window.resizable(False, False)
    window.configure(bg=BG)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(1, weight=1)

    app.form_title_lbl = tk.Label(
        window, text="Tambah tugas", font=(FONT, 19, "bold"), bg=BG, fg=NAVY)
    app.form_title_lbl.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))
    card = make_card(window)
    card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 18))
    card.columnconfigure(1, weight=1)

    app.title_var = tk.StringVar()
    app.subject_var = tk.StringVar()
    app.date_var = tk.StringVar()
    app.time_var = tk.StringVar()
    app.form_prio_var = tk.StringVar(value=PRIORITY_LABELS["Medium"])
    app.date_value = None
    app._date_picker_window = None

    def add_row(row, label, widget):
        tk.Label(card, text=label, bg=WHITE, fg=TEXT, font=(FONT, 10, "bold")).grid(
            row=row, column=0, sticky="nw", padx=(20, 12), pady=8)
        widget.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=8)

    app.title_entry = ttk.Entry(card, textvariable=app.title_var)
    add_row(0, "Judul *", app.title_entry)
    app.desc_text = tk.Text(card, height=4, font=(FONT, 10), relief="solid", borderwidth=1)
    add_row(1, "Deskripsi", app.desc_text)
    add_row(2, "Kategori", ttk.Entry(card, textvariable=app.subject_var))
    date_field = tk.Frame(card, bg=WHITE)
    date_field.columnconfigure(0, weight=1)
    app.date_entry = ttk.Entry(
        date_field, textvariable=app.date_var, state="readonly")
    app.date_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
    app.date_picker_button = ttk.Button(
        date_field, text="Pilih tanggal", style="Ghost.TButton",
        command=lambda: _open_date_picker(app._form_window, app),
    )
    app.date_picker_button.grid(row=0, column=1, sticky="e")
    add_row(3, "Tanggal *", date_field)
    add_row(4, "Jam (HH:MM) *", ttk.Entry(card, textvariable=app.time_var))
    add_row(5, "Prioritas *", ttk.Combobox(
        card,
        textvariable=app.form_prio_var,
        values=[PRIORITY_LABELS[priority] for priority in PRIORITIES],
        state="readonly",
    ))

    buttons = tk.Frame(card, bg=WHITE)
    buttons.grid(row=6, column=1, sticky="w", pady=16)
    ttk.Button(buttons, text="Simpan", style="Primary.TButton", command=app.save_task).pack(
        side="left", padx=(0, 8))
    ttk.Button(buttons, text="Batal", style="Ghost.TButton", command=app.cancel_form).pack(
        side="left")
    window.bind("<Escape>", lambda _event: app.cancel_form())
    return window
