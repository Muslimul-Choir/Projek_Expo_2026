"""Widget builder untuk halaman pengingat."""
import tkinter as tk
from tkinter import ttk

from gui.theme import BG, WHITE, NAVY, MUTED, FONT, make_card, page_header, make_tree


def build_reminder_page(parent, app):
    page = tk.Frame(parent, bg=BG)
    page.columnconfigure(0, weight=1)
    page.rowconfigure(2, weight=1)
    page_header(page, "Pengingat", "Pantau tugas yang mendekati tenggat atau terlambat").grid(
        row=0, column=0, sticky="w", pady=(0, 8))
    app.reminder_info_label = tk.Label(
        page, text="", font=(FONT, 10), bg=BG, fg=MUTED, justify="left")
    app.reminder_info_label.grid(
        row=1, column=0, sticky="w", pady=(0, 8))

    body = tk.Frame(page, bg=BG)
    body.grid(row=2, column=0, sticky="nsew")
    body.columnconfigure(0, weight=1)
    body.rowconfigure((0, 1), weight=1, uniform="r")
    columns = [
        ("title", "Tugas"), ("subject", "Kategori"),
        ("deadline", "Tenggat"), ("left", "Sisa waktu"),
    ]
    app.soon_title_label, app.soon_tree = _section(body, 0, columns)
    app.overdue_title_label, app.over_tree = _section(body, 1, columns)

    ttk.Button(page, text="Periksa sekarang", style="Primary.TButton",
               command=app.check_now).grid(row=3, column=0, sticky="w", pady=(10, 0))
    return page


def _section(parent, section_row, columns):
    card = make_card(parent)
    card.grid(
        row=section_row,
        column=0,
        sticky="nsew",
        pady=(0 if section_row == 0 else 8, 0),
    )
    card.columnconfigure(0, weight=1)
    card.rowconfigure(1, weight=1)
    title_label = tk.Label(
        card, text="", font=(FONT, 12, "bold"), bg=WHITE, fg=NAVY)
    title_label.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
    table_frame, task_tree = make_tree(
        card, columns, [240, 160, 140, 140], height=4)
    table_frame.grid(
        row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    return title_label, task_tree
