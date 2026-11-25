"""ReminderManager: memeriksa deadline & mencegah popup yang sama berulang."""
from datetime import datetime


class ReminderManager:
    def __init__(self, task_manager, soon_hours=24):
        self._manager = task_manager
        self._soon_hours = soon_hours
        self._notified = set()   # {(task_id, jenis, deadline)} yang sudah di-popup

    @property
    def soon_hours(self):
        return self._soon_hours

    def get_overdue(self, now=None):
        return self._manager.overdue_tasks(now)

    def get_due_soon(self, now=None):
        return self._manager.due_soon(now, self._soon_hours)

    def collect_new_alerts(self, now=None):
        """Kembalikan (overdue_baru, soon_baru) yang belum pernah di-popup.
        Kunci memuat deadline, jadi jika deadline diubah pengingat muncul lagi."""
        now = now or datetime.now()
        new_overdue = self._collect_unnotified(
            self.get_overdue(now), "overdue")
        new_soon = self._collect_unnotified(
            self.get_due_soon(now), "soon")
        return new_overdue, new_soon

    def _collect_unnotified(self, tasks, alert_type):
        new_tasks = []
        for task in tasks:
            key = (task.task_id, alert_type, task.deadline)
            if key not in self._notified:
                self._notified.add(key)
                new_tasks.append(task)
        return new_tasks

    def reset(self):
        self._notified.clear()

    @staticmethod
    def build_message(overdue_tasks, soon_tasks, now=None):
        now = now or datetime.now()
        lines = []
        if overdue_tasks:
            lines.append("TUGAS TERLAMBAT:")
            lines += [
                f"  - {task.title} ({task.subject}) - {task.time_left_text(now)}"
                for task in overdue_tasks
            ]
        if soon_tasks:
            if lines:
                lines.append("")
            lines.append("TENGGAT WAKTU MENDEKAT:")
            lines += [
                f"  - {task.title} ({task.subject}) - {task.deadline_text()} "
                f"({task.time_left_text(now)})"
                for task in soon_tasks
            ]
        return "\n".join(lines)
