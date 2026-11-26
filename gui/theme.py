"""Tema warna dan helper widget bersama."""
import tkinter as tk
from tkinter import ttk

NAVY, BLUE, BG, WHITE = "#17365D", "#2563EB", "#F4F8FF", "#FFFFFF"
GREEN, RED, ORANGE = "#39866A", "#C85D68", "#C98547"
TEXT, MUTED, BORDER = "#26364B", "#718096", "#DCE7F5"
PURPLE_LIGHT, ORANGE_LIGHT, BLUE_LIGHT = "#EAF2FF", "#FBF1E7", "#EAF2F8"
RED_LIGHT, HOVER_LIGHT, BLUE_HOVER = "#FAEDEF", "#E7F0FF", "#1D4ED8"
BLUE_ACCENT, ORANGE_DARK = "#4F8FEA", "#8C5928"
SIDEBAR_ACTIVE, SIDEBAR_HOVER = "#214A7A", "#1D3E68"
SIDEBAR_DIVIDER, SIDEBAR_TEXT, SIDEBAR_MUTED = "#36577F", "#EAF2FF", "#B9CCE5"

PRIORITY_COLORS = {"High": RED, "Medium": ORANGE, "Low": GREEN}
PRIORITY_LABELS = {"High": "Tinggi", "Medium": "Sedang", "Low": "Rendah"}
STATUS_LABELS = {"Pending": "Belum selesai", "Completed": "Selesai"}
FONT = "Segoe UI"


def setup_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview", rowheight=28, font=(FONT, 10), background=WHITE,
                    fieldbackground=WHITE, borderwidth=0)
    style.configure("TaskList.Treeview", rowheight=34, font=(FONT, 10),
                    background=WHITE, fieldbackground=WHITE, borderwidth=0)
    style.configure("Treeview.Heading", font=(FONT, 10, "bold"), background=NAVY,
                    foreground=WHITE, relief="flat")
    style.map("Treeview.Heading", background=[("active", BLUE)])
    style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", WHITE)])

    for name, color, hover in (
        ("Primary", BLUE, BLUE_HOVER),
        ("Success", GREEN, "#2F7058"),
        ("Danger", RED, "#AA4A55"),
        ("Navy", NAVY, "#214A7A"),
    ):
        style.configure(f"{name}.TButton", background=color, foreground=WHITE,
                        font=(FONT, 10, "bold"), padding=(12, 6), borderwidth=0)
        style.map(f"{name}.TButton", background=[("active", hover)])

    style.configure("Ghost.TButton", background=BORDER, foreground=TEXT,
                    font=(FONT, 10, "bold"), padding=(12, 6), borderwidth=0)
    style.map("Ghost.TButton", background=[("active", HOVER_LIGHT)])


def make_card(parent, **options):
    return tk.Frame(parent, bg=WHITE, highlightbackground=BORDER,
                    highlightthickness=1, **options)


def page_header(parent, title, subtitle=""):
    frame = tk.Frame(parent, bg=BG)
    tk.Label(frame, text=title, font=(FONT, 20, "bold"), bg=BG, fg=NAVY).pack(anchor="w")
    if subtitle:
        tk.Label(frame, text=subtitle, font=(FONT, 10), bg=BG, fg=MUTED).pack(anchor="w")
    return frame


def make_tree(parent, columns, widths, height=6):
    """Buat tabel Treeview + scrollbar; kembalikan (frame, tree)."""
    frame = tk.Frame(parent, bg=WHITE)
    tree = ttk.Treeview(frame, columns=[col_id for col_id, _ in columns],
                        show="headings", height=height, selectmode="browse")
    for (col_id, label), width in zip(columns, widths):
        tree.heading(col_id, text=label)
        tree.column(col_id, width=width, minwidth=40, anchor="w", stretch=True)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    tree.tag_configure("overdue", background=RED_LIGHT, foreground=RED)
    tree.tag_configure("soon", background=ORANGE_LIGHT, foreground=ORANGE_DARK)
    tree.tag_configure("done", foreground=MUTED)
    return frame, tree


def center_window(window, parent):
    """Posisikan jendela popup di tengah jendela induk."""
    window.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - window.winfo_width()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - window.winfo_height()) // 2
    window.geometry(f"+{max(x, 0)}+{max(y, 0)}")
