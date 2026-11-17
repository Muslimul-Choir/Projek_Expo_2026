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
        new_overdue, new_soon = [], []
        for t in self.get_overdue(now):
            key = (t.task_id, "overdue", t.deadline)
            if key not in self._notified:
                self._notified.add(key)
                new_overdue.append(t)
        for t in self.get_due_soon(now):
            key = (t.task_id, "soon", t.deadline)
            if key not in self._notified:
                self._notified.add(key)
                new_soon.append(t)
        return new_overdue, new_soon

    def reset(self):
        self._notified.clear()

    @staticmethod
    def build_message(overdue, soon, now=None):
        now = now or datetime.now()
        lines = []
        if overdue:
            lines.append("TUGAS TERLAMBAT:")
            lines += [f"  - {t.title} ({t.subject}) - {t.time_left_text(now)}" for t in overdue]
        if soon:
            if lines:
                lines.append("")
            lines.append("TENGGAT WAKTU MENDEKAT:")
            lines += [f"  - {t.title} ({t.subject}) - {t.deadline_text()} ({t.time_left_text(now)})" for t in soon]
        return "\n".join(lines)
