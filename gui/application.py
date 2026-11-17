"""Pengendali aplikasi Smart To-Do."""
import os
import tkinter as tk
from calendar import monthrange
from datetime import datetime
from tkinter import messagebox

from core.reminder_manager import ReminderManager
from core.task_manager import TaskManager
from gui.dashboard import MONTHS_SHORT, build_dashboard, render_calendar
from gui.focus_page import build_focus_page
from gui.reminder_page import build_reminder_page
from gui.sidebar import build_sidebar, set_active_sidebar_item
from gui.task_page import build_task_form_window, build_task_page
from gui.theme import (
    BG, PRIORITY_COLORS, PRIORITY_LABELS, STATUS_LABELS, setup_styles,
)
from utils.validators import ValidationError, validate_task_form, validate_task_id

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")
LEGACY_DATA_FILE = os.path.join(PROJECT_DIR, "tasks.json")


class SmartTodoApp(tk.Tk):
    CHECK_INTERVAL_MS = 30_000

    def __init__(self):
        super().__init__()
        self.title("Smart To-Do | Pengelola Tugas")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG)
        setup_styles(self)

        self.manager = TaskManager()
        self._form_window = None
        self._date_picker_window = None
        self.date_value = None
        self.editing_id = None
        self._load_data()
        self.reminder = ReminderManager(self.manager)
        self.manager.add_listener(self._on_data_changed)

        self._build_layout()
        self.pages = {
            "dashboard": build_dashboard(self.content, self),
            "tasks": build_task_page(self.content, self),
            "focus": build_focus_page(self.content, self),
            "reminder": build_reminder_page(self.content, self),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
        self.show_page("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._closing = False
        self._reminder_after = self.after(1500, self._reminder_tick)

    def _load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                self.manager.load_json(DATA_FILE)
            elif os.path.exists(LEGACY_DATA_FILE):
                self.manager.load_json(LEGACY_DATA_FILE)
                self._save_data()
            else:
                self.manager.load_sample_data()
        except (OSError, ValueError, TypeError, KeyError) as error:
            messagebox.showerror(
                "Gagal memuat data",
                f"File data tidak bisa dibaca ({error}). Memulai dari kosong.",
            )
            self.manager = TaskManager()

    def _save_data(self):
        try:
            self.manager.save_json(DATA_FILE)
        except OSError as error:
            messagebox.showerror("Gagal menyimpan", f"Data tidak bisa disimpan: {error}")

    def _on_data_changed(self):
        self._save_data()
        if hasattr(self, "pages"):
            self.refresh_all()

    def _on_close(self):
        self._closing = True
        self.cancel_form()
        if self._reminder_after is not None:
            try:
                self.after_cancel(self._reminder_after)
            except tk.TclError:
                pass
            self._reminder_after = None
        self._save_data()
        self.destroy()

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        sidebar = build_sidebar(self, self)
        sidebar.grid(row=0, column=0, sticky="ns")

        self.content = tk.Frame(self, bg=BG)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def show_page(self, name):
        self._refresh_page(name)
        self.pages[name].tkraise()
        set_active_sidebar_item(self, name)

    def open_form(self, task=None):
        if self._form_window is None or not self._form_window.winfo_exists():
            self._form_window = build_task_form_window(self, self)
            self._form_window.transient(self)
            self._form_window.protocol("WM_DELETE_WINDOW", self.cancel_form)

        self.editing_id = task.task_id if task else None
        self._form_window.title("Ubah tugas" if task else "Tambah tugas")
        self.form_title_lbl.config(text="Ubah tugas" if task else "Tambah tugas")
        self.title_var.set(task.title if task else "")
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", task.description if task else "")
        self.subject_var.set(task.subject if task else "")
        self.date_value = task.deadline.date() if task else None
        self.date_var.set(self.date_value.isoformat() if self.date_value else "")
        self.time_var.set(task.deadline.strftime("%H:%M") if task else "23:59")
        self.form_prio_var.set(
            PRIORITY_LABELS[task.priority] if task else PRIORITY_LABELS["Medium"])
        self._form_window.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - self._form_window.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - self._form_window.winfo_height()) // 2
        self._form_window.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self._form_window.lift()
        self._form_window.grab_set()
        self.title_entry.focus_set()

    def add_task(self):
        self.open_form()

    def save_task(self):
        try:
            date_value = self.date_value
            if date_value is None or self.date_var.get() != date_value.isoformat():
                date_value = self.date_var.get()
            data = validate_task_form(
                self.title_var.get(),
                self.desc_text.get("1.0", "end"),
                self.subject_var.get(),
                date_value,
                self.time_var.get(),
                self.form_prio_var.get(),
            )
            if self.editing_id is None:
                self.manager.add_task(**data)
                message = "Tugas baru berhasil ditambahkan."
            else:
                self.manager.edit_task(self.editing_id, **data)
                message = "Tugas berhasil diperbarui."
        except ValidationError as error:
            messagebox.showerror("Input tidak valid", str(error))
            return
        except KeyError as error:
            messagebox.showerror("Gagal", str(error))
            return
        messagebox.showinfo("Berhasil", message)
        self.cancel_form()

    def cancel_form(self):
        window, self._form_window = self._form_window, None
        self.editing_id = None
        self.date_value = None
        if self._date_picker_window is not None:
            self._date_picker_window.destroy()
            self._date_picker_window = None
        if window is None:
            return
        try:
            if window.winfo_exists():
                window.grab_release()
                window.destroy()
        except tk.TclError:
            pass

    def _selected_id(self):
        selection = self.task_tree.selection()
        if not selection:
            return None
        return validate_task_id(selection[0])

    def _selected_task(self):
        try:
            task_id = self._selected_id()
            if task_id is None:
                raise ValidationError("Pilih salah satu tugas dulu di tabel.")
            task = self.manager.find_by_id(task_id)
            if task is None:
                raise ValidationError(f"Tugas dengan ID {task_id} tidak ditemukan.")
            return task
        except ValidationError as error:
            messagebox.showerror("Gagal", str(error))
            return None

    def edit_selected_task(self):
        task = self._selected_task()
        if task is not None:
            self.open_form(task)

    def view_selected_task(self):
        task = self._selected_task()
        if task is not None:
            self.view_task(task)

    def view_task(self, task):
        messagebox.showinfo(
            "Detail Tugas",
            f"ID: {task.task_id}\nJudul: {task.title}\n"
            f"Deskripsi: {task.description or '-'}\n"
            f"Kategori: {task.subject}\n"
            f"Tenggat waktu: {task.deadline_text()} ({task.time_left_text()})\n"
            f"Prioritas: {PRIORITY_LABELS[task.priority]}\n"
            f"Status: {STATUS_LABELS[task.status]}\n"
            f"Dibuat: {task.created.strftime('%Y-%m-%d %H:%M')}",
        )

    def complete_selected_task(self):
        task = self._selected_task()
        if task is None:
            return
        if task.is_completed():
            messagebox.showinfo("Info", "Tugas ini sudah ditandai selesai.")
            return
        try:
            self.manager.complete_task(task.task_id)
        except KeyError as error:
            messagebox.showerror("Gagal", f"Tidak bisa menyelesaikan tugas: {error}")
            return
        messagebox.showinfo("Berhasil", f"Tugas '{task.title}' ditandai selesai.")

    def delete_selected_task(self):
        task = self._selected_task()
        if task is None or not messagebox.askyesno("Konfirmasi", f"Hapus tugas '{task.title}'?"):
            return
        try:
            self.manager.delete_task(task.task_id)
        except KeyError as error:
            messagebox.showerror("Gagal", f"Tidak bisa menghapus tugas: {error}")
            return
        messagebox.showinfo("Berhasil", "Tugas berhasil dihapus.")

    def refresh_all(self):
        for name in ("dashboard", "tasks", "focus", "reminder"):
            self._refresh_page(name)

    def _refresh_page(self, name):
        refreshers = {
            "dashboard": self._refresh_dashboard,
            "tasks": self._refresh_tasks,
            "focus": self._refresh_focus,
            "reminder": self._refresh_reminders,
        }
        refreshers[name]()

    def _refresh_dashboard(self):
        stats = self.manager.statistics()
        stats["due_soon"] = len(self.manager.due_soon(hours=24))
        for key, label in self._stat_labels.items():
            label.config(text=str(stats[key]))

        self.upcoming_tree.delete(*self.upcoming_tree.get_children())
        for task in self.manager.upcoming(limit=5):
            self.upcoming_tree.insert(
                "", "end", iid=str(task.task_id),
                values=(task.title, task.subject, task.deadline_text()),
            )
        render_calendar(self)
        self._refresh_calendar_tasks()

    def _change_calendar_month(self, offset):
        month_index = self._calendar_month.month - 1 + offset
        year = self._calendar_month.year + month_index // 12
        month = month_index % 12 + 1
        day = min(self._calendar_selected.day, monthrange(year, month)[1])
        self._calendar_month = self._calendar_month.replace(year=year, month=month, day=1)
        self._calendar_selected = self._calendar_selected.replace(
            year=year, month=month, day=day)
        render_calendar(self)
        self._refresh_calendar_tasks()

    def _select_calendar_date(self, selected):
        self._calendar_selected = selected
        self._calendar_month = selected.replace(day=1)
        render_calendar(self)
        self._refresh_calendar_tasks()

    def _refresh_calendar_tasks(self):
        selected = self._calendar_selected
        title = "Tugas hari ini" if selected == datetime.now().date() else (
            f"Tugas {selected.day} {MONTHS_SHORT[selected.month - 1]}")
        self._day_tasks_title.config(text=title)
        self.day_task_tree.delete(*self.day_task_tree.get_children())
        tasks = [task for task in self.manager.tasks if task.deadline.date() == selected]
        for task in self.manager.sorted_by_deadline(tasks):
            self.day_task_tree.insert(
                "", "end", iid=str(task.task_id),
                values=(task.title, task.subject, task.deadline.strftime("%H:%M")),
                tags=("done",) if task.is_completed() else (),
            )
        self._day_tasks_empty.config(text="" if tasks else "Tidak ada tugas pada tanggal ini.")

    def _refresh_tasks(self):
        selection = self.task_tree.selection()
        selected_id = int(selection[0]) if selection else None
        self.task_tree.delete(*self.task_tree.get_children())
        status_filter = {
            "Semua": "All",
            "Belum selesai": "Pending",
            "Selesai": "Completed",
        }[self.status_var.get()]
        priority_filter = {
            "Semua": "All",
            **{label: value for value, label in PRIORITY_LABELS.items()},
        }[self.prio_var.get()]
        tasks = self.manager.search(
            self.search_var.get(), status_filter, priority_filter)
        for task in tasks:
            alert = task.alert_label(hours=self.reminder.soon_hours)
            alert_text = "Terlambat" if alert == "Overdue" else alert
            tag = (
                "done" if task.is_completed()
                else "overdue" if alert == "Overdue"
                else "soon" if alert in ("Hari ini", "Segera")
                else f"p_{task.priority}"
            )
            self.task_tree.insert(
                "", "end", iid=str(task.task_id), tags=(tag,),
                values=(
                    task.title, task.subject, task.deadline_text(),
                    PRIORITY_LABELS[task.priority], STATUS_LABELS[task.status], alert_text,
                ),
            )
        self.task_count_lbl.config(text=f"{len(tasks)} tugas")
        if selected_id is not None and self.task_tree.exists(str(selected_id)):
            self.task_tree.selection_set(str(selected_id))

    def _refresh_focus(self):
        task = self._focus_current = self.manager.recommend_next()
        if task is None:
            self.focus_done_icon.pack(anchor="w", pady=(0, 4))
            self.focus_title_lbl.config(text="Semua tugas sudah selesai")
            self.focus_info_lbl.config(
                text="Tidak ada tugas yang perlu diselesaikan. Tambahkan tugas baru atau beristirahat dulu.")
            self.focus_prio_lbl.config(text="")
            self.focus_left_lbl.config(text="")
            self.focus_button.state(["disabled"])
            return

        self.focus_button.state(["!disabled"])
        self.focus_done_icon.pack_forget()
        self.focus_title_lbl.config(text=task.title)
        self.focus_info_lbl.config(
            text=f"Kategori      : {task.subject}\nTenggat waktu: {task.deadline_text()}\n"
            f"Deskripsi: {task.description or '-'}")
        self.focus_prio_lbl.config(
            text=f"Prioritas: {PRIORITY_LABELS[task.priority]}",
            fg=PRIORITY_COLORS[task.priority])
        self.focus_left_lbl.config(text=task.time_left_text())

    def complete_focus_task(self):
        task = self.manager.find_by_id(self._focus_current.task_id) if self._focus_current else None
        if task is None:
            messagebox.showinfo("Info", "Tidak ada tugas yang direkomendasikan.")
            return
        try:
            self.manager.complete_task(task.task_id)
        except KeyError as error:
            messagebox.showerror("Gagal", str(error))
            return
        messagebox.showinfo("Berhasil", f"Mantap! '{task.title}' selesai.")

    def _refresh_reminders(self):
        soon = self.reminder.get_due_soon()
        overdue = self.reminder.get_overdue()
        self.reminder_info_lbl.config(
            text=f"Pemeriksaan otomatis setiap {self.CHECK_INTERVAL_MS // 1000} detik. "
            f"Pengingat muncul saat tenggat kurang dari {self.reminder.soon_hours} jam lagi.")
        self.soon_title.config(text=f"Mendekati tenggat ({len(soon)})")
        self.over_title.config(text=f"Terlambat ({len(overdue)})")
        for tree, tasks, tag in (
            (self.soon_tree, soon, "soon"),
            (self.over_tree, overdue, "overdue"),
        ):
            tree.delete(*tree.get_children())
            for task in tasks:
                tree.insert(
                    "", "end",
                    values=(task.title, task.subject, task.deadline_text(), task.time_left_text()),
                    tags=(tag,),
                )

    def check_now(self):
        self._refresh_reminders()
        self.reminder.reset()
        self.run_reminder_check(force_info=True)

    def run_reminder_check(self, force_info=False):
        overdue, soon = self.reminder.collect_new_alerts()
        if overdue or soon:
            messagebox.showwarning(
                "Pengingat tenggat",
                ReminderManager.build_message(overdue, soon),
            )
        elif force_info:
            messagebox.showinfo(
                "Pengingat",
                "Tidak ada tugas yang mendekati tenggat atau terlambat.",
            )
        self._refresh_reminders()

    def _reminder_tick(self):
        if self._closing:
            return
        try:
            self.run_reminder_check()
        except (OSError, ValueError, KeyError, tk.TclError) as error:
            messagebox.showerror("Pengingat", f"Pengecekan pengingat gagal: {error}")
        if not self._closing:
            self._reminder_after = self.after(self.CHECK_INTERVAL_MS, self._reminder_tick)
