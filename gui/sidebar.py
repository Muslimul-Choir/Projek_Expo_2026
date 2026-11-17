"""Pembangun dan penata navigasi sidebar."""
import tkinter as tk

from gui.theme import (
    BLUE, FONT, NAVY, SIDEBAR_ACTIVE, SIDEBAR_HOVER, SIDEBAR_MUTED,
    SIDEBAR_DIVIDER, SIDEBAR_TEXT, WHITE,
)

NAV_ITEMS = (
    ("dashboard", "Ringkasan"),
    ("tasks", "Daftar tugas"),
    ("focus", "Mode fokus"),
    ("reminder", "Pengingat"),
)


def build_sidebar(parent, app):
    sidebar = tk.Frame(parent, bg=NAVY, width=224)
    sidebar.grid_propagate(False)
    sidebar.rowconfigure(3, weight=1)

    brand = tk.Frame(sidebar, bg=NAVY)
    brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 22))
    logo = tk.Canvas(brand, width=40, height=40, bg=NAVY, highlightthickness=0)
    logo.pack(side="left", padx=(0, 10))
    _draw_logo(logo)
    brand_text = tk.Frame(brand, bg=NAVY)
    brand_text.pack(side="left", fill="y")
    tk.Label(
        brand_text, text="Smart To-Do", font=(FONT, 15, "bold"),
        bg=NAVY, fg=WHITE,
    ).pack(anchor="w", pady=(1, 0))
    tk.Label(
        brand_text, text="Rencana, lebih teratur", font=(FONT, 8),
        bg=NAVY, fg=SIDEBAR_MUTED,
    ).pack(anchor="w")

    tk.Frame(sidebar, bg=SIDEBAR_DIVIDER, height=1).grid(
        row=1, column=0, sticky="ew", padx=18)
    tk.Label(
        sidebar, text="MENU", font=(FONT, 8, "bold"),
        bg=NAVY, fg=SIDEBAR_MUTED,
    ).grid(row=2, column=0, sticky="w", padx=22, pady=(22, 8))

    navigation = tk.Frame(sidebar, bg=NAVY)
    navigation.grid(row=3, column=0, sticky="new", padx=12)
    app.nav_buttons = {}
    for key, title in NAV_ITEMS:
        row = tk.Frame(navigation, bg=NAVY, height=44)
        row.pack(fill="x", pady=3)
        row.pack_propagate(False)
        indicator = tk.Frame(row, bg=NAVY, width=3)
        indicator.pack(side="left", fill="y", padx=(0, 8))
        content = tk.Frame(row, bg=NAVY)
        content.pack(side="left", fill="both", expand=True)
        icon = tk.Canvas(content, width=22, height=22, bg=NAVY, highlightthickness=0)
        icon.pack(side="left", padx=(9, 12))
        label = tk.Label(
            content, text=title, font=(FONT, 10, "bold"),
            bg=NAVY, fg=SIDEBAR_TEXT,
        )
        label.pack(side="left")
        app.nav_buttons[key] = {
            "row": row,
            "indicator": indicator,
            "content": content,
            "icon": icon,
            "label": label,
        }

        for widget in (row, indicator, content, icon, label):
            widget.bind("<Button-1>", lambda event, name=key: _navigate(event, app, name))
            widget.bind("<Enter>", lambda _event, name=key: _hover_item(app, name, True))
            widget.bind("<Leave>", lambda _event, name=key: _hover_item(app, name, False))

    footer = tk.Frame(sidebar, bg=NAVY)
    footer.grid(row=4, column=0, sticky="sew", padx=20, pady=18)
    tk.Frame(footer, bg=SIDEBAR_DIVIDER, height=1).pack(fill="x", pady=(0, 12))
    tk.Label(
        footer, text="Semua tugas, satu tempat.", font=(FONT, 9),
        bg=NAVY, fg=SIDEBAR_MUTED,
    ).pack(anchor="w")
    return sidebar


def set_active_sidebar_item(app, active_key):
    app._active_page = active_key
    for key, item in app.nav_buttons.items():
        active = key == active_key
        background = SIDEBAR_ACTIVE if active else NAVY
        item["row"].configure(bg=background)
        item["indicator"].configure(bg=BLUE if active else NAVY)
        item["content"].configure(bg=background)
        item["icon"].configure(bg=background)
        item["label"].configure(bg=background, fg=WHITE if active else SIDEBAR_TEXT)
        _draw_nav_icon(item["icon"], key, WHITE if active else SIDEBAR_MUTED)


def _hover_item(app, key, hovering):
    if key == app._active_page:
        return
    item = app.nav_buttons[key]
    background = SIDEBAR_HOVER if hovering else NAVY
    item["row"].configure(bg=background)
    item["content"].configure(bg=background)
    item["icon"].configure(bg=background)
    item["label"].configure(bg=background)


def _navigate(_event, app, key):
    app.show_page(key)
    return "break"


def _draw_logo(canvas):
    canvas.create_rectangle(1, 1, 39, 39, fill=BLUE, outline="")
    canvas.create_line(11, 12, 14, 15, 19, 9, fill=WHITE, width=2)
    canvas.create_line(23, 12, 31, 12, fill=WHITE, width=2)
    canvas.create_line(11, 25, 14, 28, 19, 22, fill=WHITE, width=2)
    canvas.create_line(23, 25, 31, 25, fill=WHITE, width=2)


def _draw_nav_icon(canvas, key, color):
    canvas.delete("all")
    if key == "dashboard":
        for x, y in ((3, 3), (13, 3), (3, 13), (13, 13)):
            canvas.create_rectangle(x, y, x + 6, y + 6, outline=color, width=1.6)
    elif key == "tasks":
        for y in (5, 11, 17):
            canvas.create_rectangle(3, y - 2, 6, y + 1, outline=color, width=1.4)
            canvas.create_line(10, y, 20, y, fill=color, width=1.6)
    elif key == "focus":
        for radius in (8, 5, 2):
            canvas.create_oval(
                11 - radius, 11 - radius, 11 + radius, 11 + radius,
                outline=color, width=1.5,
            )
    else:
        canvas.create_line(6, 16, 16, 16, 19, 19, 3, 19, 6, 16,
                          fill=color, width=1.6, joinstyle="round")
        canvas.create_arc(5, 2, 17, 16, start=0, extent=180,
                          style="arc", outline=color, width=1.6)
        canvas.create_line(5, 9, 5, 16, fill=color, width=1.6)
        canvas.create_line(17, 9, 17, 16, fill=color, width=1.6)
        canvas.create_oval(9, 20, 13, 22, fill=color, outline=color)
