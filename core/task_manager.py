"""TaskManager: CRUD, pencarian rekursif, statistik, pengurutan, Focus Mode."""
import json
import os
from datetime import datetime, timedelta

from models.task import Task, PRIORITY_RANK


class TaskManager:
    def __init__(self):
        self._tasks = []        # List of Task (data hanya di memori)
        self._next_id = 1
        self._listeners = []    # observer: dipanggil tiap data berubah

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify(self):
        for listener in self._listeners:
            listener()

    # ---------- fungsi rekursif (Role 01) ----------
    @staticmethod
    def _binary_search(tasks, task_id, first_index, last_index):
        """Pencarian biner REKURSIF. List selalu terurut menurut ID
        karena ID bertambah terus saat tugas ditambahkan."""
        if first_index > last_index:
            return None
        middle_index = (first_index + last_index) // 2
        middle_task = tasks[middle_index]
        if middle_task.task_id == task_id:
            return middle_task
        if middle_task.task_id < task_id:
            return TaskManager._binary_search(
                tasks, task_id, middle_index + 1, last_index)
        return TaskManager._binary_search(
            tasks, task_id, first_index, middle_index - 1)

    def find_by_id(self, task_id):
        return self._binary_search(self._tasks, task_id, 0, len(self._tasks) - 1)

    # ---------- CRUD ----------
    @property
    def tasks(self):
        return list(self._tasks)

    def add_task(self, title, description, subject, deadline, priority):
        task = Task(self._next_id, title, description, subject, deadline, priority)
        self._next_id += 1
        self._tasks.append(task)
        self._notify()
        return task

    def _get_or_raise(self, task_id):
        task = self.find_by_id(task_id)
        if task is None:
            raise KeyError(f"Tugas dengan ID {task_id} tidak ditemukan.")
        return task

    def edit_task(self, task_id, title, description, subject, deadline, priority):
        task = self._get_or_raise(task_id)
        task.title = title
        task.description = description
        task.subject = subject
        task.deadline = deadline
        task.priority = priority
        self._notify()
        return task

    def delete_task(self, task_id):
        self._tasks.remove(self._get_or_raise(task_id))
        self._notify()

    def complete_task(self, task_id):
        task = self._get_or_raise(task_id)
        task.complete()
        self._notify()
        return task

    # ---------- pengurutan, pencarian, filter ----------
    def sorted_by_deadline(self, tasks=None):
        return sorted(self._tasks if tasks is None else tasks,
                      key=lambda task: (task.deadline, PRIORITY_RANK[task.priority]))

    def search(self, keyword="", status="All", priority="All"):
        normalized_keyword = (keyword or "").strip().lower()
        matching_tasks = []
        for task in self._tasks:
            if status != "All" and task.status != status:
                continue
            if priority != "All" and task.priority != priority:
                continue
            searchable_fields = (task.title, task.subject, task.description)
            if normalized_keyword and all(
                normalized_keyword not in field.lower()
                for field in searchable_fields
            ):
                continue
            matching_tasks.append(task)
        return self.sorted_by_deadline(matching_tasks)

    # ---------- deteksi deadline ----------
    def overdue_tasks(self, now=None):
        current_time = now or datetime.now()
        overdue_tasks = [
            task for task in self._tasks if task.is_overdue(current_time)
        ]
        return self.sorted_by_deadline(overdue_tasks)

    def due_soon(self, now=None, hours=24):
        current_time = now or datetime.now()
        tasks_due_soon = [
            task for task in self._tasks
            if task.is_due_soon(current_time, hours)
        ]
        return self.sorted_by_deadline(tasks_due_soon)

    def upcoming(self, now=None, limit=5):
        current_time = now or datetime.now()
        upcoming_tasks = [
            task for task in self._tasks
            if not task.is_completed() and task.deadline >= current_time
        ]
        return self.sorted_by_deadline(upcoming_tasks)[:limit]

    # ---------- statistik ----------
    def statistics(self, now=None):
        current_time = now or datetime.now()
        pending_tasks = [
            task for task in self._tasks if not task.is_completed()
        ]
        return {
            "total": len(self._tasks),
            "completed": len(self._tasks) - len(pending_tasks),
            "pending": len(pending_tasks),
            "overdue": sum(
                1 for task in pending_tasks if task.is_overdue(current_time)
            ),
            "due_today": sum(
                1 for task in pending_tasks if task.is_due_today(current_time)
            ),
            "priority": {
                priority_name: sum(
                    1 for task in pending_tasks
                    if task.priority == priority_name
                )
                for priority_name in PRIORITY_RANK
            },
        }

    # ---------- Focus Mode ----------
    def recommend_next(self):
        """Pending saja; urut deadline terdekat, lalu prioritas tertinggi."""
        pending_tasks = [
            task for task in self._tasks if not task.is_completed()
        ]
        if not pending_tasks:
            return None
        return min(
            pending_tasks,
            key=lambda task: (task.deadline, PRIORITY_RANK[task.priority]),
        )

    # ---------- penyimpanan opsional (JSON, bukan database) ----------
    def save_json(self, path):
        json_data = {
            "next_id": self._next_id,
            "tasks": [task.to_dict() for task in self._tasks],
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=2, ensure_ascii=False)

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
        loaded_tasks = sorted(
            (Task.from_dict(task_data) for task_data in json_data["tasks"]),
            key=lambda task: task.task_id,
        )
        self._tasks = loaded_tasks
        stored_next_id = int(json_data.get("next_id", 1))
        next_available_id = (
            loaded_tasks[-1].task_id + 1 if loaded_tasks else 1
        )
        self._next_id = max(stored_next_id, next_available_id)
        self._notify()

    def load_sample_data(self):
        current_time = datetime.now().replace(second=0, microsecond=0)
        sample_tasks = [
            ("Kirim proposal", "Periksa lampiran sebelum dikirim", "Pekerjaan",
             current_time + timedelta(hours=5), "High"),
            ("Belanja kebutuhan", "Beli kebutuhan mingguan", "Pribadi",
             current_time + timedelta(days=1), "Medium"),
            ("Periksa kendaraan", "Cek oli dan tekanan ban", "Rumah",
             current_time + timedelta(days=2), "Low"),
            ("Bayar tagihan internet", "Jatuh tempo pembayaran bulanan", "Keuangan",
             current_time + timedelta(days=3), "Medium"),
            ("Rencanakan akhir pekan", "Tentukan kegiatan dan jadwal", "Pribadi",
             current_time + timedelta(days=6), "Low"),
        ]
        for title, description, subject, deadline, priority in sample_tasks:
            self.add_task(title, description, subject, deadline, priority)
