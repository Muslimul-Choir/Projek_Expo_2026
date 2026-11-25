"""Pengujian logika inti. Jalankan: python -m unittest discover -s tests -v"""
import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reminder_manager import ReminderManager
from core.task_manager import TaskManager
from models.task import BaseTask, Task
from utils import validators

FIXED_NOW = datetime(2026, 11, 3, 12, 0)


def create_task(
    task_manager, title="Example task", deadline=None, priority="Medium"
):
    task_deadline = deadline or FIXED_NOW + timedelta(days=2)
    return task_manager.add_task(
        title, "", "Course", task_deadline, priority)


class TestValidators(unittest.TestCase):
    def test_title(self):
        with self.assertRaises(validators.ValidationError):
            validators.validate_title("   ")
        self.assertEqual(validators.validate_title(" Halo "), "Halo")

    def test_date_and_time(self):
        invalid_dates = ("2026-13-01", "2026-02-30", "15-11-2026", "abc", "")
        for invalid_date in invalid_dates:
            with self.assertRaises(validators.ValidationError):
                validators.validate_date(invalid_date)

        invalid_times = ("24:00", "12:60", "9:00", "xx")
        for invalid_time in invalid_times:
            with self.assertRaises(validators.ValidationError):
                validators.validate_time(invalid_time)

        expected_deadline = datetime(2026, 11, 15, 23, 59)
        self.assertEqual(
            validators.validate_deadline("2026-11-15", "23:59"),
            expected_deadline,
        )
        self.assertEqual(
            validators.validate_date(date(2026, 11, 15)),
            date(2026, 11, 15),
        )
        self.assertEqual(
            validators.validate_deadline(
                date(2026, 11, 15), "23:59"),
            expected_deadline,
        )

    def test_priority_and_task_id(self):
        self.assertEqual(validators.validate_priority("high"), "High")
        self.assertEqual(validators.validate_priority("Tinggi"), "High")
        with self.assertRaises(validators.ValidationError):
            validators.validate_priority("Urgent")
        with self.assertRaises(validators.ValidationError):
            validators.validate_task_id("abc")
        with self.assertRaises(validators.ValidationError):
            validators.validate_task_id(0)
        self.assertEqual(validators.validate_task_id(" 7 "), 7)

    def test_description_can_be_empty(self):
        self.assertEqual(validators.validate_description(None), "")


class TestTaskModel(unittest.TestCase):
    def test_inheritance_and_polymorphism(self):
        task = Task(1, "Example", "", "Course", FIXED_NOW, "High")
        self.assertIsInstance(task, BaseTask)
        self.assertNotEqual(BaseTask(1, "Example").describe(), task.describe())

    def test_properties_validate_values(self):
        task = Task(1, "Example", "", "Course", FIXED_NOW, "High")
        with self.assertRaises(ValueError):
            task.priority = "X"
        with self.assertRaises(ValueError):
            task.title = ""


class TestTaskCRUD(unittest.TestCase):
    def setUp(self):
        self.task_manager = TaskManager()

    def test_add_edit_delete_and_complete(self):
        task = create_task(self.task_manager, "First task")
        self.task_manager.edit_task(
            task.task_id, "Updated task", "Details", "Course", FIXED_NOW, "Low")
        self.assertEqual((task.title, task.priority), ("Updated task", "Low"))

        self.task_manager.complete_task(task.task_id)
        self.assertTrue(task.is_completed())
        self.task_manager.delete_task(task.task_id)
        self.assertEqual(len(self.task_manager.tasks), 0)

    def test_missing_task_id_raises_error(self):
        for operation in (
            self.task_manager.delete_task,
            self.task_manager.complete_task,
        ):
            with self.assertRaises(KeyError):
                operation(99)

    def test_data_change_notifies_listeners(self):
        notifications = []
        self.task_manager.add_listener(lambda: notifications.append(True))
        task = create_task(self.task_manager)
        self.task_manager.complete_task(task.task_id)
        self.assertEqual(len(notifications), 2)

    def test_search_filters_by_keyword_status_and_priority(self):
        create_task(
            self.task_manager, "Python report", priority="High")
        completed_task = create_task(
            self.task_manager, "Quiz", priority="Low")
        self.task_manager.complete_task(completed_task.task_id)

        self.assertEqual(len(self.task_manager.search("python")), 1)
        self.assertEqual(
            len(self.task_manager.search(status="Completed")), 1)
        self.assertEqual(
            len(self.task_manager.search(priority="High")), 1)


class TestTaskLookup(unittest.TestCase):
    def test_find_task_by_id(self):
        task_manager = TaskManager()
        task_ids = [
            create_task(task_manager, f"Task {index}").task_id
            for index in range(200)
        ]

        for task_id in (task_ids[0], task_ids[57], task_ids[-1]):
            self.assertEqual(
                task_manager.find_by_id(task_id).task_id, task_id)
        self.assertIsNone(task_manager.find_by_id(9999))
        self.assertIsNone(TaskManager().find_by_id(1))

    def test_find_tasks_after_deletion(self):
        task_manager = TaskManager()
        create_task(task_manager)
        task_to_delete = create_task(task_manager)
        task_after_deleted_task = create_task(task_manager)

        task_manager.delete_task(task_to_delete.task_id)

        self.assertIsNone(task_manager.find_by_id(task_to_delete.task_id))
        self.assertIs(
            task_manager.find_by_id(task_after_deleted_task.task_id),
            task_after_deleted_task,
        )


class TestTaskDeadlines(unittest.TestCase):
    def test_deadline_detection_and_statistics(self):
        task_manager = TaskManager()
        create_task(
            task_manager, "Overdue", FIXED_NOW - timedelta(hours=2), "High")
        create_task(
            task_manager, "Due today", FIXED_NOW + timedelta(hours=3))
        create_task(
            task_manager, "Due later", FIXED_NOW + timedelta(days=5), "Low")
        completed_task = create_task(
            task_manager, "Completed overdue", FIXED_NOW - timedelta(days=1))
        task_manager.complete_task(completed_task.task_id)

        statistics = task_manager.statistics(FIXED_NOW)
        self.assertEqual(
            (
                statistics["total"],
                statistics["completed"],
                statistics["pending"],
                statistics["overdue"],
                statistics["due_today"],
            ),
            (4, 1, 3, 1, 1),
        )
        self.assertEqual(
            [task.title for task in task_manager.overdue_tasks(FIXED_NOW)],
            ["Overdue"],
        )
        self.assertEqual(
            [task.title for task in task_manager.upcoming(FIXED_NOW)],
            ["Due today", "Due later"],
        )
        self.assertEqual(task_manager.sorted_by_deadline()[0].title, "Completed overdue")

    def test_focus_recommends_nearest_deadline_and_highest_priority(self):
        task_manager = TaskManager()
        self.assertIsNone(task_manager.recommend_next())
        create_task(task_manager, "Low priority", FIXED_NOW, "Low")
        create_task(task_manager, "High priority", FIXED_NOW, "High")
        create_task(
            task_manager, "Later deadline", FIXED_NOW + timedelta(days=1), "High")

        self.assertEqual(task_manager.recommend_next().title, "High priority")
        task_manager.complete_task(task_manager.recommend_next().task_id)
        self.assertEqual(task_manager.recommend_next().title, "Low priority")


class TestReminders(unittest.TestCase):
    def test_alerts_are_not_repeated_for_same_deadline(self):
        task_manager = TaskManager()
        reminder_manager = ReminderManager(task_manager)
        due_soon_task = create_task(
            task_manager, "Due soon", FIXED_NOW + timedelta(hours=2))
        create_task(task_manager, "Overdue", FIXED_NOW - timedelta(hours=1))

        overdue_alerts, soon_alerts = reminder_manager.collect_new_alerts(FIXED_NOW)
        self.assertEqual((len(overdue_alerts), len(soon_alerts)), (1, 1))

        overdue_alerts, soon_alerts = reminder_manager.collect_new_alerts(FIXED_NOW)
        self.assertEqual((len(overdue_alerts), len(soon_alerts)), (0, 0))

        task_manager.edit_task(
            due_soon_task.task_id,
            "Due soon",
            "",
            "Course",
            FIXED_NOW + timedelta(hours=3),
            "Medium",
        )
        self.assertEqual(
            len(reminder_manager.collect_new_alerts(FIXED_NOW)[1]), 1)
        self.assertIn(
            "TUGAS TERLAMBAT",
            ReminderManager.build_message(
                task_manager.overdue_tasks(FIXED_NOW), [], now=FIXED_NOW),
        )


class TestTaskJSON(unittest.TestCase):
    def test_save_and_load_preserves_task_data_and_next_id(self):
        task_manager = TaskManager()
        create_task(task_manager, "First task")
        completed_task = create_task(task_manager, "Second task")
        task_manager.complete_task(completed_task.task_id)
        json_path = os.path.join(tempfile.mkdtemp(), "tasks.json")
        task_manager.save_json(json_path)

        loaded_task_manager = TaskManager()
        loaded_task_manager.load_json(json_path)
        self.assertEqual(
            [(task.title, task.status) for task in loaded_task_manager.tasks],
            [("First task", "Pending"), ("Second task", "Completed")],
        )
        self.assertEqual(
            create_task(loaded_task_manager, "Third task").task_id, 3)

    def test_save_creates_parent_directory(self):
        task_manager = TaskManager()
        create_task(task_manager, "Saved in data folder")
        json_path = os.path.join(
            tempfile.mkdtemp(), "data", "tasks.json")

        task_manager.save_json(json_path)

        self.assertTrue(os.path.isfile(json_path))


if __name__ == "__main__":
    unittest.main()
