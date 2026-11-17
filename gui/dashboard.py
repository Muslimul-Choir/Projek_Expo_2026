"""Widget builder untuk dashboard overview, kalender, dan tugas harian."""
import calendar
import tkinter as tk
from datetime import date

from gui.theme import (
    BG, WHITE, NAVY, BLUE, BLUE_ACCENT, MUTED, TEXT, FONT,
    make_card, make_tree,
    PURPLE_LIGHT, BLUE_LIGHT, HOVER_LIGHT, BLUE_HOVER,
)

CARD_TINTS = (BLUE_LIGHT, "#F2F7FF", "#E7F0FF", "#F2F7FF")
CARD_ACCENTS = (BLUE, BLUE_ACCENT, BLUE, BLUE_ACCENT)
WEEKDAYS = ("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")
MONTHS = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)
MONTHS_SHORT = (
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
)


def build_dashboard(parent, app):
    page = tk.Frame(parent, bg=BG)
    page.columnconfigure(0, weight=1)
    page.rowconfigure(1, weight=1)

    heading = tk.Frame(page, bg=BG)
    heading.grid(row=0, column=0, sticky="ew", pady=(0, 14))
    tk.Label(heading, text="Halo!", font=(FONT, 11), bg=BG, fg=MUTED).pack(anchor="w")
    tk.Label(heading, text="Ringkasan aktivitasmu", font=(FONT, 22, "bold"),
             bg=BG, fg=NAVY).pack(anchor="w")

    content = tk.Frame(page, bg=BG)
    content.grid(row=1, column=0, sticky="nsew")
    content.columnconfigure(0, weight=1, uniform="dashboard")
    content.columnconfigure(1, weight=1, uniform="dashboard")
    content.rowconfigure(0, weight=1)

    _build_overview(content, app)
    _build_calendar_and_day_tasks(content, app)
    app._calendar_month = date.today().replace(day=1)
    app._calendar_selected = date.today()
    return page


def _build_overview(parent, app):
    overview = tk.Frame(parent, bg=BG)
    overview.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    overview.columnconfigure((0, 1), weight=1, uniform="stats")
    overview.rowconfigure(3, weight=1)

    tk.Label(overview, text="Ringkasan", font=(FONT, 17, "bold"),
             bg=BG, fg=NAVY).grid(row=0, column=0, sticky="w", pady=(0, 10))
    app._stat_labels = {}
    stat_cards = (
        ("due_today", "Hari ini", CARD_TINTS[0], CARD_ACCENTS[0]),
        ("due_soon", "Segera", CARD_TINTS[1], CARD_ACCENTS[1]),
        ("completed", "Selesai", CARD_TINTS[2], CARD_ACCENTS[2]),
        ("total", "Semua tugas", CARD_TINTS[3], CARD_ACCENTS[3]),
    )
    for index, (key, title, tint, accent) in enumerate(stat_cards):
        row, column = divmod(index, 2)
        card = tk.Frame(overview, bg=tint, padx=14, pady=10)
        card.grid(row=1 + row, column=column, sticky="nsew",
                  padx=(0, 6) if column == 0 else (6, 0), pady=(0, 10))
        value = tk.Label(card, text="0", font=(FONT, 22, "bold"), bg=tint, fg=NAVY)
        value.pack(anchor="w")
        tk.Label(card, text=title, font=(FONT, 9), bg=tint, fg=TEXT).pack(anchor="w")
        tk.Frame(card, bg=accent, height=3).pack(fill="x", pady=(7, 0))
        app._stat_labels[key] = value

    upcoming = make_card(overview)
    upcoming.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(2, 0))
    upcoming.columnconfigure(0, weight=1)
    upcoming.rowconfigure(1, weight=1)
    tk.Label(upcoming, text="Tugas mendatang", font=(FONT, 12, "bold"),
             bg=WHITE, fg=NAVY).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
    frame, app.upcoming_tree = make_tree(
        upcoming,
        [("title", "Tugas"), ("subject", "Kategori"), ("deadline", "Tenggat")],
        [150, 100, 105],
        height=5,
    )
    frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    app.upcoming_tree.bind("<Double-1>", lambda _event: _open_selected_upcoming(app))


def _build_calendar_and_day_tasks(parent, app):
    panel = tk.Frame(parent, bg=BG)
    panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    panel.columnconfigure(0, weight=1)
    panel.rowconfigure(1, weight=1)

    calendar_card = make_card(panel)
    calendar_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
    calendar_card.columnconfigure(0, weight=1)
    controls = tk.Frame(calendar_card, bg=WHITE)
    controls.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
    controls.columnconfigure(1, weight=1)
    tk.Button(
        controls, text="‹", font=(FONT, 14), width=3, relief="flat",
        bg=WHITE, fg=NAVY, activebackground=PURPLE_LIGHT,
        command=lambda: app._change_calendar_month(-1),
    ).grid(row=0, column=0, sticky="w")
    app._calendar_month_label = tk.Label(
        controls, text="", font=(FONT, 12, "bold"), bg=WHITE, fg=NAVY)
    app._calendar_month_label.grid(row=0, column=1)
    tk.Button(
        controls, text="›", font=(FONT, 14), width=3, relief="flat",
        bg=WHITE, fg=NAVY, activebackground=PURPLE_LIGHT,
        command=lambda: app._change_calendar_month(1),
    ).grid(row=0, column=2, sticky="e")

    app._calendar_grid = tk.Frame(calendar_card, bg=WHITE)
    app._calendar_grid.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
    for column, weekday in enumerate(WEEKDAYS):
        app._calendar_grid.columnconfigure(column, weight=1, uniform="weekday")
        tk.Label(app._calendar_grid, text=weekday, font=(FONT, 9, "bold"),
                 bg=WHITE, fg=MUTED).grid(row=0, column=column, sticky="ew", pady=(2, 4))

    day_card = make_card(panel)
    day_card.grid(row=1, column=0, sticky="nsew")
    day_card.columnconfigure(0, weight=1)
    day_card.rowconfigure(1, weight=1)
    day_header = tk.Frame(day_card, bg=WHITE)
    day_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
    day_header.columnconfigure(0, weight=1)
    app._day_tasks_title = tk.Label(
        day_header, text="Tugas hari ini", font=(FONT, 13, "bold"), bg=WHITE, fg=NAVY)
    app._day_tasks_title.grid(row=0, column=0, sticky="w")
    tk.Button(
        day_header, text="+", font=(FONT, 16, "bold"), width=2, relief="flat",
        bg=BLUE, fg=WHITE, activebackground=BLUE_HOVER, activeforeground=WHITE,
        command=app.add_task,
    ).grid(row=0, column=1)
    frame, app.day_task_tree = make_tree(
        day_card,
        [("title", "Tugas"), ("subject", "Kategori"), ("time", "Jam")],
        [155, 95, 70],
        height=6,
    )
    frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    app.day_task_tree.bind("<Double-1>", lambda _event: _open_selected_day_task(app))
    app._day_tasks_empty = tk.Label(
        day_card, text="", font=(FONT, 9), bg=WHITE, fg=MUTED)
    app._day_tasks_empty.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 8))


def render_calendar(app):
    month = app._calendar_month
    app._calendar_month_label.config(text=f"{MONTHS[month.month - 1]} {month.year}")
    for widget in app._calendar_grid.grid_slaves():
        if int(widget.grid_info()["row"]) > 0:
            widget.destroy()

    deadlines = {task.deadline.date() for task in app.manager.tasks}
    weeks = calendar.monthcalendar(month.year, month.month)
    for week_index, week in enumerate(weeks, start=1):
        for column, day in enumerate(week):
            if not day:
                continue
            selected = date(month.year, month.month, day)
            is_selected = selected == app._calendar_selected
            is_today = selected == date.today()
            has_tasks = selected in deadlines
            text = f"{day}\n{'•' if has_tasks else ' '}"
            background = BLUE if is_selected else WHITE
            foreground = WHITE if is_selected else NAVY
            if is_today and not is_selected:
                background, foreground = PURPLE_LIGHT, BLUE_HOVER
            button = tk.Button(
                app._calendar_grid, text=text, font=(FONT, 9, "bold"),
                width=4, height=2, relief="flat", bd=0,
                bg=background, fg=foreground, activebackground=HOVER_LIGHT,
                activeforeground=NAVY,
                command=lambda selected_date=selected: app._select_calendar_date(selected_date),
            )
            button.grid(row=week_index, column=column, sticky="nsew", padx=2, pady=1)


def _open_selected_upcoming(app):
    selection = app.upcoming_tree.selection()
    if selection:
        task = app.manager.find_by_id(int(selection[0]))
        if task is not None:
            app.view_task(task)


def _open_selected_day_task(app):
    selection = app.day_task_tree.selection()
    if selection:
        task = app.manager.find_by_id(int(selection[0]))
        if task is not None:
            app.view_task(task)
