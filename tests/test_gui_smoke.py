"""Smoke test GUI: buat jendela, navigasi semua halaman, uji alur CRUD lewat widget.
Butuh display (di Linux: xvfb-run python -m unittest tests.test_gui_smoke)."""
import os, sys, tempfile, unittest
from datetime import date, datetime, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gui.application as app_module
import main as entrypoint
from gui.theme import BLUE, NAVY, SIDEBAR_ACTIVE


class TestGUI(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.mkdtemp()
        app_module.DATA_FILE = os.path.join(temp_dir, "data", "tasks.json")
        app_module.LEGACY_DATA_FILE = os.path.join(temp_dir, "legacy.json")
        self.mb = {n: mock.patch.object(app_module.messagebox, n, return_value=True).start()
                   for n in ("showinfo", "showerror", "showwarning", "askyesno")}
        self.app = app_module.SmartTodoApp()
        self.app.update()

    def tearDown(self):
        if not self.app._closing:
            self.app._on_close()
        mock.patch.stopall()

    def test_dashboard_first_and_navigation(self):
        self.assertIs(entrypoint.SmartTodoApp, app_module.SmartTodoApp)
        self.assertNotIn("form", self.app.pages)
        self.assertEqual(self.app.pages["dashboard"].winfo_manager(), "grid")
        dashboard_nav = self.app.nav_buttons["dashboard"]
        self.assertEqual(dashboard_nav["indicator"].cget("bg"), BLUE)
        self.assertGreater(len(dashboard_nav["icon"].find_all()), 0)
        for key in ("dashboard", "tasks", "focus", "reminder"):
            self.app.show_page(key); self.app.update()
        self.assertEqual(self.app.nav_buttons["reminder"]["row"].cget("bg"), SIDEBAR_ACTIVE)
        self.assertEqual(self.app.nav_buttons["dashboard"]["row"].cget("bg"), NAVY)

    def test_legacy_data_migrates_to_data_folder(self):
        temp_dir = tempfile.mkdtemp()
        legacy_path = os.path.join(temp_dir, "tasks.json")
        data_path = os.path.join(temp_dir, "data", "tasks.json")
        original_paths = app_module.DATA_FILE, app_module.LEGACY_DATA_FILE
        legacy_manager = app_module.TaskManager()
        legacy_manager.add_task(
            "Legacy task", "", "Personal", datetime(2030, 1, 1), "Low")
        legacy_manager.save_json(legacy_path)
        try:
            app_module.DATA_FILE = data_path
            app_module.LEGACY_DATA_FILE = legacy_path
            self.app.manager = app_module.TaskManager()
            self.app._load_data()
            self.assertTrue(os.path.isfile(data_path))
            self.assertEqual(self.app.manager.tasks[0].title, "Legacy task")
        finally:
            app_module.DATA_FILE, app_module.LEGACY_DATA_FILE = original_paths

    def test_add_validation_and_crud(self):
        m = self.app.manager
        n = len(m.tasks)
        self.app.open_form(None)
        form_window = self.app._form_window
        self.assertTrue(form_window.winfo_exists())
        self.assertLess(form_window.winfo_width(), self.app.winfo_width())
        self.app.title_var.set(""); self.app.save_task()
        self.mb["showerror"].assert_called()
        self.assertEqual(len(m.tasks), n)
        self.app.title_var.set("Tugas Uji")
        self.app.date_var.set("2026-02-30")
        self.app.save_task()
        self.assertEqual(len(m.tasks), n)
        self.app.date_var.set("2030-01-01")
        self.app.time_var.set("10:00")
        self.app.save_task()
        self.assertEqual(len(m.tasks), n + 1)
        self.assertIsNone(self.app._form_window)

        self.app._refresh_tasks()
        new_id = m.tasks[-1].task_id
        self.app.task_tree.selection_set(str(new_id))
        self.app.edit_selected_task()
        self.app.title_var.set("Tugas Uji 2")
        self.app.save_task()
        self.assertEqual(m.find_by_id(new_id).title, "Tugas Uji 2")
        self.app.task_tree.selection_set(str(new_id))
        self.app.complete_selected_task()
        self.assertTrue(m.find_by_id(new_id).is_completed())
        self.app.task_tree.selection_set(str(new_id))
        self.app.delete_selected_task()
        self.assertIsNone(m.find_by_id(new_id))

    def test_no_selection_error_and_dashboard_autoupdate(self):
        self.app.task_tree.selection_set(())
        self.app.delete_selected_task()
        self.mb["showerror"].assert_called()
        before = self.app._stat_labels["total"].cget("text")
        self.app.manager.add_task("Baru", "", "MK", __import__("datetime").datetime(2030, 1, 1), "Low")
        self.assertEqual(int(self.app._stat_labels["total"].cget("text")), int(before) + 1)

    def test_focus_and_reminder(self):
        self.app._refresh_focus()
        rec = self.app.manager.recommend_next()
        self.assertEqual(self.app.focus_title_lbl.cget("text"), rec.title)
        self.assertEqual(self.app.focus_done_icon.winfo_manager(), "")
        self.app.complete_focus_task()
        self.assertTrue(rec.is_completed())
        self.app.run_reminder_check(); self.mb["showwarning"].assert_called_once()
        self.app.run_reminder_check(); self.mb["showwarning"].assert_called_once()  # tidak berulang
        self.app.check_now()

    def test_completed_state_uses_check_icon(self):
        for task in self.app.manager.tasks:
            self.app.manager.complete_task(task.task_id)
        self.app._refresh_focus()
        self.assertEqual(self.app.focus_title_lbl.cget("text"), "Semua tugas sudah selesai")
        self.assertEqual(self.app.focus_done_icon.winfo_manager(), "pack")

    def test_search_filter_widgets(self):
        self.app.search_var.set("proposal"); self.app.update()
        self.assertEqual(len(self.app.task_tree.get_children()), 1)
        self.assertEqual(self.app.task_count_lbl.cget("text"), "1 tugas")
        self.app.search_var.set(""); self.app.prio_var.set("Tinggi"); self.app.update()
        self.assertTrue(all(
            self.app.task_tree.set(item, "prio") == "Tinggi"
            for item in self.app.task_tree.get_children()
        ))

    def test_localized_priority_stays_compatible_with_model(self):
        self.app.open_form()
        self.app.title_var.set("Tugas umum")
        self.app.date_var.set("2030-01-01")
        self.app.time_var.set("10:00")
        self.app.form_prio_var.set("Tinggi")
        self.app.save_task()
        self.assertEqual(self.app.manager.tasks[-1].priority, "High")
        self.assertIsNone(self.app._form_window)

    def test_cancel_closes_form_popup_without_saving(self):
        task_count = len(self.app.manager.tasks)
        self.app.open_form()
        popup = self.app._form_window
        self.app.cancel_form()
        self.assertFalse(popup.winfo_exists())
        self.assertIsNone(self.app._form_window)
        self.assertEqual(len(self.app.manager.tasks), task_count)

    def test_date_picker_selects_date_value(self):
        self.app.open_form()
        self.assertEqual(str(self.app.date_entry.cget("state")), "readonly")
        self.app.date_picker_button.invoke()
        popup = self.app._date_picker_window
        grid = popup.winfo_children()[0].winfo_children()[1]
        today = date.today()
        today_button = next(
            widget for widget in grid.winfo_children()
            if isinstance(widget, app_module.tk.Button)
            and widget.cget("text") == str(today.day)
        )
        today_button.invoke()
        self.assertEqual(self.app.date_value, today)
        self.assertEqual(self.app.date_var.get(), today.isoformat())
        self.assertFalse(popup.winfo_exists())

    def test_calendar_selects_deadline_tasks(self):
        deadline = datetime.now() + timedelta(days=8)
        task = self.app.manager.add_task("Calendar task", "", "Study", deadline, "High")
        self.app._select_calendar_date(deadline.date())
        self.assertIn(str(task.task_id), self.app.day_task_tree.get_children())
        self.assertEqual(self.app._calendar_month, deadline.date().replace(day=1))
        self.app._change_calendar_month(1)
        self.assertNotEqual(self.app._calendar_month, deadline.date().replace(day=1))

    def test_close_cancels_reminder_timer(self):
        self.assertIsNotNone(self.app._reminder_after)
        self.app._on_close()
        self.assertIsNone(self.app._reminder_after)
        self.assertTrue(self.app._closing)


if __name__ == "__main__":
    unittest.main()
