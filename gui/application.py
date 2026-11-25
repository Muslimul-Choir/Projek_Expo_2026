"""Pengendali aplikasi Smart To-Do."""
import os
import tkinter as tk
from calendar import monthrange
from datetime import datetime
from tkinter import messagebox

from core.reminder_manager import ReminderManager
from core.task_manager import TaskManager
from gui.constants import MONTHS_SHORT
from gui.dashboard import build_dashboard, render_calendar
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

    def show_page(self, page_name):
        self._refresh_page(page_name)
        self.pages[page_name].tkraise()
        set_active_sidebar_item(self, page_name)

    def open_form(self, task=None):
        if self._form_window is None or not self._form_window.winfo_exists():
            self._form_window = build_task_form_window(self, self)
            self._form_window.transient(self)
            self._form_window.protocol("WM_DELETE_WINDOW", self.cancel_form)

        self.editing_id = task.task_id if task else None
        self._form_window.title("Ubah tugas" if task else "Tambah tugas")
        self.form_title_label.config(text="Ubah tugas" if task else "Tambah tugas")
        self.title_var.set(task.title if task else "")
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", task.description if task else "")
        self.subject_var.set(task.subject if task else "")
        self.date_value = task.deadline.date() if task else None
        self.date_var.set(self.date_value.isoformat() if self.date_value else "")
        self.time_var.set(task.deadline.strftime("%H:%M") if task else "23:59")
        self.form_priority_var.set(
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
            validated_task_data = validate_task_form(
                self.title_var.get(),
                self.description_text.get("1.0", "end"),
                self.subject_var.get(),
                date_value,
                self.time_var.get(),
                self.form_priority_var.get(),
            )
            if self.editing_id is None:
                self.manager.add_task(**validated_task_data)
                success_message = "Tugas baru berhasil ditambahkan."
            else:
                self.manager.edit_task(self.editing_id, **validated_task_data)
                success_message = "Tugas berhasil diperbarui."
        except ValidationError as error:
            messagebox.showerror("Input tidak valid", str(error))
            return
        except KeyError as error:
            messagebox.showerror("Gagal", str(error))
            return
        messagebox.showinfo("Berhasil", success_message)
        self.cancel_form()

    def cancel_form(self):
        form_window, self._form_window = self._form_window, None
        self.editing_id = None
        self.date_value = None
        if self._date_picker_window is not None:
            self._date_picker_window.destroy()
            self._date_picker_window = None
        if form_window is None:
            return
        try:
            if form_window.winfo_exists():
                form_window.grab_release()
                form_window.destroy()
        except tk.TclError:
            pass

    def _selected_id(self):
        selected_rows = self.task_tree.selection()
        if not selected_rows:
            return None
        return validate_task_id(selected_rows[0])

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
        self._complete_task(task, f"Tugas '{task.title}' ditandai selesai.")

    def _complete_task(self, task, success_message):
        try:
            self.manager.complete_task(task.task_id)
        except KeyError as error:
            messagebox.showerror("Gagal", f"Tidak bisa menyelesaikan tugas: {error}")
            return
        messagebox.showinfo("Berhasil", success_message)

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
        for page_name in ("dashboard", "tasks", "focus", "reminder"):
            self._refresh_page(page_name)

    def _refresh_page(self, page_name):
        refreshers = {
            "dashboard": self._refresh_dashboard,
            "tasks": self._refresh_tasks,
            "focus": self._refresh_focus,
            "reminder": self._refresh_reminders,
        }
        refreshers[page_name]()

    def _refresh_dashboard(self):
        task_statistics = self.manager.statistics()
        task_statistics["due_soon"] = len(self.manager.due_soon(hours=24))
        for statistic_name, statistic_label in self._stat_labels.items():
            statistic_label.config(text=str(task_statistics[statistic_name]))

        self.upcoming_tree.delete(*self.upcoming_tree.get_children())
        for task in self.manager.upcoming(limit=5):
            self.upcoming_tree.insert(
                "", "end", iid=str(task.task_id),
                values=(task.title, task.subject, task.deadline_text()),
            )
        render_calendar(self)
        self._refresh_calendar_tasks()

    def _change_calendar_month(self, month_offset):
        target_month_index = (
            self._calendar_displayed_month.month - 1 + month_offset)
        target_year = (
            self._calendar_displayed_month.year + target_month_index // 12)
        target_month = target_month_index % 12 + 1
        selected_day = min(
            self._calendar_selected_date.day,
            monthrange(target_year, target_month)[1],
        )
        self._calendar_displayed_month = self._calendar_displayed_month.replace(
            year=target_year, month=target_month, day=1)
        self._calendar_selected_date = self._calendar_selected_date.replace(
            year=target_year, month=target_month, day=selected_day)
        render_calendar(self)
        self._refresh_calendar_tasks()

    def _select_calendar_date(self, selected_date):
        self._calendar_selected_date = selected_date
        self._calendar_displayed_month = selected_date.replace(day=1)
        render_calendar(self)
        self._refresh_calendar_tasks()

    def _refresh_calendar_tasks(self):
        selected_date = self._calendar_selected_date
        section_title = (
            "Tugas hari ini"
            if selected_date == datetime.now().date()
            else f"Tugas {selected_date.day} {MONTHS_SHORT[selected_date.month - 1]}"
        )
        self._day_tasks_title_label.config(text=section_title)
        self.day_task_tree.delete(*self.day_task_tree.get_children())
        tasks_on_selected_date = [
            task for task in self.manager.tasks
            if task.deadline.date() == selected_date
        ]
        for task in self.manager.sorted_by_deadline(tasks_on_selected_date):
            self.day_task_tree.insert(
                "", "end", iid=str(task.task_id),
                values=(task.title, task.subject, task.deadline.strftime("%H:%M")),
                tags=("done",) if task.is_completed() else (),
            )
        self._day_tasks_empty_label.config(
            text="" if tasks_on_selected_date else "Tidak ada tugas pada tanggal ini.")

    def _refresh_tasks(self):
        selected_rows = self.task_tree.selection()
        selected_task_id = int(selected_rows[0]) if selected_rows else None
        self.task_tree.delete(*self.task_tree.get_children())
        status_filter = {
            "Semua": "All",
            "Belum selesai": "Pending",
            "Selesai": "Completed",
        }[self.status_filter_var.get()]
        priority_filter = {
            "Semua": "All",
            **{
                localized_priority: priority_name
                for priority_name, localized_priority in PRIORITY_LABELS.items()
            },
        }[self.priority_filter_var.get()]
        tasks = self.manager.search(
            self.search_filter_var.get(), status_filter, priority_filter)
        for task in tasks:
            alert = task.alert_label(hours=self.reminder.soon_hours)
            alert_text = "Terlambat" if alert == "Overdue" else alert
            task_tag = (
                "done" if task.is_completed()
                else "overdue" if alert == "Overdue"
                else "soon" if alert in ("Hari ini", "Segera")
                else f"p_{task.priority}"
            )
            self.task_tree.insert(
                "", "end", iid=str(task.task_id), tags=(task_tag,),
                values=(
                    task.title, task.subject, task.deadline_text(),
                    PRIORITY_LABELS[task.priority], STATUS_LABELS[task.status], alert_text,
                ),
            )
        self.task_count_label.config(text=f"{len(tasks)} tugas")
        if (
            selected_task_id is not None
            and self.task_tree.exists(str(selected_task_id))
        ):
            self.task_tree.selection_set(str(selected_task_id))

    def _refresh_focus(self):
        focus_task = self._focus_current_task = self.manager.recommend_next()
        if focus_task is None:
            self.focus_done_icon.pack(anchor="w", pady=(0, 4))
            self.focus_title_label.config(text="Semua tugas sudah selesai")
            self.focus_info_label.config(
                text="Tidak ada tugas yang perlu diselesaikan. Tambahkan tugas baru atau beristirahat dulu.")
            self.focus_priority_label.config(text="")
            self.focus_time_left_label.config(text="")
            self.focus_button.state(["disabled"])
            return

        self.focus_button.state(["!disabled"])
        self.focus_done_icon.pack_forget()
        self.focus_title_label.config(text=focus_task.title)
        self.focus_info_label.config(
            text=f"Kategori      : {focus_task.subject}\n"
            f"Tenggat waktu: {focus_task.deadline_text()}\n"
            f"Deskripsi: {focus_task.description or '-'}")
        self.focus_priority_label.config(
            text=f"Prioritas: {PRIORITY_LABELS[focus_task.priority]}",
            fg=PRIORITY_COLORS[focus_task.priority])
        self.focus_time_left_label.config(text=focus_task.time_left_text())

    def complete_focus_task(self):
        if self._focus_current_task is None:
            messagebox.showinfo("Info", "Tidak ada tugas yang direkomendasikan.")
            return
        task = self.manager.find_by_id(self._focus_current_task.task_id)
        if task is None:
            messagebox.showinfo("Info", "Tidak ada tugas yang direkomendasikan.")
            return
        self._complete_task(task, f"Mantap! '{task.title}' selesai.")

    def _refresh_reminders(self):
        tasks_due_soon = self.reminder.get_due_soon()
        overdue_tasks = self.reminder.get_overdue()
        self.reminder_info_label.config(
            text=f"Pemeriksaan otomatis setiap {self.CHECK_INTERVAL_MS // 1000} detik. "
            f"Pengingat muncul saat tenggat kurang dari {self.reminder.soon_hours} jam lagi.")
        self.soon_title_label.config(
            text=f"Mendekati tenggat ({len(tasks_due_soon)})")
        self.overdue_title_label.config(
            text=f"Terlambat ({len(overdue_tasks)})")
        for task_tree, task_list, row_tag in (
            (self.soon_tree, tasks_due_soon, "soon"),
            (self.over_tree, overdue_tasks, "overdue"),
        ):
            task_tree.delete(*task_tree.get_children())
            for task in task_list:
                task_tree.insert(
                    "", "end",
                    values=(task.title, task.subject, task.deadline_text(), task.time_left_text()),
                    tags=(row_tag,),
                )

    def check_now(self):
        self._refresh_reminders()
        self.reminder.reset()
        self.run_reminder_check(force_info=True)

    def run_reminder_check(self, force_info=False):
        overdue_tasks, soon_tasks = self.reminder.collect_new_alerts()
        if overdue_tasks or soon_tasks:
            messagebox.showwarning(
                "Pengingat tenggat",
                ReminderManager.build_message(overdue_tasks, soon_tasks),
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
