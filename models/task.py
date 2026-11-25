"""Model data: BaseTask (parent class) dan Task (child class)."""
from datetime import datetime, timedelta

PRIORITIES = ("High", "Medium", "Low")
STATUSES = ("Pending", "Completed")
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}  # makin kecil makin penting
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class BaseTask:
    """Parent class: atribut dasar sebuah tugas (encapsulation lewat property)."""

    def __init__(self, task_id, title, description=""):
        self._task_id = task_id
        self._title = title
        self._description = description

    @property
    def task_id(self):
        return self._task_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        title = (title or "").strip()
        if not title:
            raise ValueError("Judul tugas tidak boleh kosong.")
        self._title = title

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = (description or "").strip()

    def describe(self):
        return f"#{self._task_id} {self._title}"

    def __str__(self):
        return self.describe()


class Task(BaseTask):
    """Child class: menambahkan kategori, tenggat, prioritas, dan status."""

    def __init__(self, task_id, title, description, subject, deadline,
                 priority, status="Pending", created=None):
        super().__init__(task_id, title, description)
        self._subject = subject
        self._deadline = deadline
        self._priority = "Medium"
        self._status = "Pending"
        self.priority = priority
        self.status = status
        self._created = created or datetime.now()

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, subject):
        self._subject = (subject or "").strip() or "Umum"

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, deadline):
        if not isinstance(deadline, datetime):
            raise ValueError("Tenggat waktu harus bertipe datetime.")
        self._deadline = deadline

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority):
        if priority not in PRIORITIES:
            raise ValueError("Prioritas tidak valid.")
        self._priority = priority

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status not in STATUSES:
            raise ValueError("Status tidak valid.")
        self._status = status

    @property
    def created(self):
        return self._created

    def complete(self):
        self._status = "Completed"

    def is_completed(self):
        return self._status == "Completed"

    def is_overdue(self, now=None):
        now = now or datetime.now()
        return (not self.is_completed()) and self._deadline < now

    def is_due_today(self, now=None):
        now = now or datetime.now()
        # Hari ini & belum lewat jam deadline (yang sudah lewat dihitung Overdue).
        return (not self.is_completed()) and self._deadline.date() == now.date() \
            and self._deadline >= now

    def is_due_soon(self, now=None, hours=24):
        now = now or datetime.now()
        if self.is_completed() or self._deadline < now:
            return False
        return self._deadline - now <= timedelta(hours=hours)

    def alert_label(self, now=None, hours=24):
        """Penanda khusus untuk tabel: Overdue / Hari ini / Segera / ''."""
        if self.is_overdue(now):
            return "Overdue"
        if self.is_due_today(now):
            return "Hari ini"
        if self.is_due_soon(now, hours):
            return "Segera"
        return ""

    def time_left_text(self, now=None):
        now = now or datetime.now()
        if self.is_completed():
            return "Selesai"
        time_difference = self._deadline - now
        total_seconds = int(abs(time_difference.total_seconds()))
        days, remaining_seconds = divmod(total_seconds, 86400)
        hours, remaining_seconds = divmod(remaining_seconds, 3600)
        minutes = remaining_seconds // 60
        if days:
            text = f"{days} hari {hours} jam"
        elif hours:
            text = f"{hours} jam {minutes} menit"
        else:
            text = f"{minutes} menit"
        if time_difference.total_seconds() < 0:
            return f"Terlambat {text}"
        return f"{text} lagi"

    def deadline_text(self):
        return self._deadline.strftime(DATETIME_FORMAT)

    def describe(self):  # polymorphism: override BaseTask.describe
        return f"#{self._task_id} [{self._priority}] {self._title} ({self._subject}) - {self.deadline_text()}"

    def to_dict(self):
        return {
            "id": self._task_id, "title": self._title, "description": self._description,
            "subject": self._subject,
            "deadline": self._deadline.strftime(DATETIME_FORMAT),
            "priority": self._priority, "status": self._status,
            "created": self._created.strftime(DATETIME_FORMAT),
        }

    @classmethod
    def from_dict(cls, task_data):
        return cls(
            int(task_data["id"]),
            task_data["title"],
            task_data.get("description", ""),
            task_data.get("subject", "Umum"),
            datetime.strptime(task_data["deadline"], DATETIME_FORMAT),
            task_data.get("priority", "Medium"),
            task_data.get("status", "Pending"),
            datetime.strptime(task_data["created"], DATETIME_FORMAT),
        )
