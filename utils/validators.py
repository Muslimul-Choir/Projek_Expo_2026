"""Validasi input pengguna; kesalahan validasi memakai ValueError."""
import re
from datetime import date, datetime

from models.task import PRIORITIES


ValidationError = ValueError


def validate_title(title):
    title = (title or "").strip()
    if not title:
        raise ValidationError("Judul tugas tidak boleh kosong.")
    if len(title) > 100:
        raise ValidationError("Judul tugas maksimal 100 karakter.")
    return title


def validate_description(description):
    # Deskripsi boleh kosong.
    return (description or "").strip()


def validate_subject(subject):
    return (subject or "").strip() or "Umum"


def validate_date(date_value):
    if isinstance(date_value, datetime):
        return date_value.date()
    if isinstance(date_value, date):
        return date_value
    if not isinstance(date_value, str):
        raise ValidationError("Format tanggal harus YYYY-MM-DD, contoh: 2026-11-15.")
    date_text = date_value.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
        raise ValidationError("Format tanggal harus YYYY-MM-DD, contoh: 2026-11-15.")
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Tanggal tidak valid (cek bulan dan harinya).")


def validate_time(time_value):
    time_text = (time_value or "").strip()
    if not re.fullmatch(r"\d{2}:\d{2}", time_text):
        raise ValidationError("Format jam harus HH:MM (24 jam), contoh: 23:59.")
    try:
        return datetime.strptime(time_text, "%H:%M").time()
    except ValueError:
        raise ValidationError("Jam tidak valid (00:00 - 23:59).")


def validate_deadline(date_text, time_text):
    return datetime.combine(validate_date(date_text), validate_time(time_text))


def validate_priority(priority):
    priority = (priority or "").strip().capitalize()
    priority = {"Tinggi": "High", "Sedang": "Medium", "Rendah": "Low"}.get(
        priority, priority)
    if priority not in PRIORITIES:
        raise ValidationError("Prioritas harus Tinggi, Sedang, atau Rendah.")
    return priority


def validate_task_id(task_id):
    try:
        task_id = int(str(task_id).strip())
    except (TypeError, ValueError):
        raise ValidationError("ID tugas harus berupa angka.")
    if task_id <= 0:
        raise ValidationError("ID tugas harus lebih dari 0.")
    return task_id


def validate_task_form(title, description, subject, date_text, time_text, priority):
    """Validasi seluruh isi form; mengembalikan dict bersih."""
    return {
        "title": validate_title(title),
        "description": validate_description(description),
        "subject": validate_subject(subject),
        "deadline": validate_deadline(date_text, time_text),
        "priority": validate_priority(priority),
    }
