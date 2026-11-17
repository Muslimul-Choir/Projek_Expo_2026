"""Pengujian logika inti (Role 04). Jalankan: python -m unittest discover -s tests -v"""
import os, sys, tempfile, unittest
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.reminder_manager import ReminderManager
from core.task_manager import TaskManager
from models.task import BaseTask, Task
from utils import validators as v

NOW = datetime(2026, 11, 3, 12, 0)


def make(m, title="T", dl=None, prio="Medium"):
    return m.add_task(title, "", "MK", dl or NOW + timedelta(days=2), prio)


class TestValidators(unittest.TestCase):
    def test_title(self):
        with self.assertRaises(v.ValidationError): v.validate_title("   ")
        self.assertEqual(v.validate_title(" Halo "), "Halo")

    def test_date_time(self):
        for bad in ("2026-13-01", "2026-02-30", "15-11-2026", "abc", ""):
            with self.assertRaises(v.ValidationError): v.validate_date(bad)
        for bad in ("24:00", "12:60", "9:00", "xx"):
            with self.assertRaises(v.ValidationError): v.validate_time(bad)
        self.assertEqual(v.validate_deadline("2026-11-15", "23:59"), datetime(2026, 11, 15, 23, 59))
        self.assertEqual(v.validate_date(date(2026, 11, 15)), date(2026, 11, 15))
        self.assertEqual(
            v.validate_deadline(date(2026, 11, 15), "23:59"),
            datetime(2026, 11, 15, 23, 59),
        )

    def test_priority_and_id(self):
        self.assertEqual(v.validate_priority("high"), "High")
        self.assertEqual(v.validate_priority("Tinggi"), "High")
        with self.assertRaises(v.ValidationError): v.validate_priority("Urgent")
        with self.assertRaises(v.ValidationError): v.validate_task_id("abc")
        with self.assertRaises(v.ValidationError): v.validate_task_id(0)
        self.assertEqual(v.validate_task_id(" 7 "), 7)

    def test_description_optional(self):
        self.assertEqual(v.validate_description(None), "")


class TestOOP(unittest.TestCase):
    def test_inheritance_polymorphism(self):
        t = Task(1, "A", "", "MK", NOW, "High")
        self.assertIsInstance(t, BaseTask)
        self.assertNotEqual(BaseTask(1, "A").describe(), t.describe())

    def test_encapsulation(self):
        t = Task(1, "A", "", "MK", NOW, "High")
        with self.assertRaises(ValueError): t.priority = "X"
        with self.assertRaises(ValueError): t.title = ""


class TestCRUD(unittest.TestCase):
    def setUp(self):
        self.m = TaskManager()

    def test_add_edit_delete_complete(self):
        t = make(self.m, "Satu")
        self.m.edit_task(t.task_id, "Dua", "d", "X", NOW, "Low")
        self.assertEqual((t.title, t.priority), ("Dua", "Low"))
        self.m.complete_task(t.task_id)
        self.assertTrue(t.is_completed())
        self.m.delete_task(t.task_id)
        self.assertEqual(len(self.m.tasks), 0)

    def test_missing_id(self):
        for fn in (self.m.delete_task, self.m.complete_task):
            with self.assertRaises(KeyError): fn(99)

    def test_listener_called(self):
        calls = []
        self.m.add_listener(lambda: calls.append(1))
        t = make(self.m); self.m.complete_task(t.task_id)
        self.assertEqual(len(calls), 2)

    def test_search_filter(self):
        make(self.m, "Laporan Python", prio="High")
        b = make(self.m, "Kuis", prio="Low"); self.m.complete_task(b.task_id)
        self.assertEqual(len(self.m.search("python")), 1)
        self.assertEqual(len(self.m.search(status="Completed")), 1)
        self.assertEqual(len(self.m.search(priority="High")), 1)


class TestRecursive(unittest.TestCase):
    def test_find_by_id(self):
        m = TaskManager()
        ids = [make(m, f"t{i}").task_id for i in range(200)]
        for i in (ids[0], ids[57], ids[-1]):
            self.assertEqual(m.find_by_id(i).task_id, i)
        self.assertIsNone(m.find_by_id(9999))
        self.assertIsNone(TaskManager().find_by_id(1))

    def test_after_delete(self):
        m = TaskManager()
        a, b, c = make(m), make(m), make(m)
        m.delete_task(b.task_id)
        self.assertIsNone(m.find_by_id(b.task_id))
        self.assertIs(m.find_by_id(c.task_id), c)


class TestDeadline(unittest.TestCase):
    def test_detection_and_stats(self):
        m = TaskManager()
        make(m, "lewat", NOW - timedelta(hours=2), "High")
        make(m, "hari ini", NOW + timedelta(hours=3))
        make(m, "jauh", NOW + timedelta(days=5), "Low")
        d = make(m, "done", NOW - timedelta(days=1)); m.complete_task(d.task_id)
        s = m.statistics(NOW)
        self.assertEqual((s["total"], s["completed"], s["pending"], s["overdue"], s["due_today"]), (4, 1, 3, 1, 1))
        self.assertEqual([t.title for t in m.overdue_tasks(NOW)], ["lewat"])
        self.assertEqual([t.title for t in m.upcoming(NOW)], ["hari ini", "jauh"])
        self.assertEqual(m.sorted_by_deadline()[0].title, "done")

    def test_focus(self):
        m = TaskManager()
        self.assertIsNone(m.recommend_next())
        make(m, "low", NOW, "Low"); make(m, "high", NOW, "High"); make(m, "later", NOW + timedelta(days=1), "High")
        self.assertEqual(m.recommend_next().title, "high")
        m.complete_task(m.recommend_next().task_id)
        self.assertEqual(m.recommend_next().title, "low")


class TestReminder(unittest.TestCase):
    def test_no_duplicate_popup(self):
        m = TaskManager(); r = ReminderManager(m)
        t = make(m, "x", NOW + timedelta(hours=2)); make(m, "y", NOW - timedelta(hours=1))
        o, s = r.collect_new_alerts(NOW)
        self.assertEqual((len(o), len(s)), (1, 1))
        o, s = r.collect_new_alerts(NOW)
        self.assertEqual((len(o), len(s)), (0, 0))
        m.edit_task(t.task_id, "x", "", "MK", NOW + timedelta(hours=3), "Medium")
        self.assertEqual(len(r.collect_new_alerts(NOW)[1]), 1)
        self.assertIn("TUGAS TERLAMBAT", ReminderManager.build_message(*(m.overdue_tasks(NOW), []), now=NOW))


class TestJSON(unittest.TestCase):
    def test_roundtrip(self):
        m = TaskManager(); make(m, "a"); b = make(m, "b"); m.complete_task(b.task_id)
        p = os.path.join(tempfile.mkdtemp(), "t.json"); m.save_json(p)
        m2 = TaskManager(); m2.load_json(p)
        self.assertEqual([(t.title, t.status) for t in m2.tasks], [("a", "Pending"), ("b", "Completed")])
        self.assertEqual(make(m2, "c").task_id, 3)

    def test_save_creates_parent_directory(self):
        manager = TaskManager()
        make(manager, "Saved in data folder")
        path = os.path.join(tempfile.mkdtemp(), "data", "tasks.json")
        manager.save_json(path)
        self.assertTrue(os.path.isfile(path))


if __name__ == "__main__":
    unittest.main()
