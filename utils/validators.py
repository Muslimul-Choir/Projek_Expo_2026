"""Validasi input pengguna; kesalahan validasi memakai ValueError."""
import re
from datetime import date, datetime

from models.task import PRIORITIES


ValidationError = ValueError


def validate_title(value):
    value = (value or "").strip()
    if not value:
        raise ValidationError("Judul tugas tidak boleh kosong.")
    if len(value) > 100:
        raise ValidationError("Judul tugas maksimal 100 karakter.")
    return value


def validate_description(value):
    # Deskripsi boleh kosong.
    return (value or "").strip()


def validate_subject(value):
    value = (value or "").strip()
    return value if value else "Umum"


def validate_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValidationError("Format tanggal harus YYYY-MM-DD, contoh: 2026-11-15.")
    value = value.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValidationError("Format tanggal harus YYYY-MM-DD, contoh: 2026-11-15.")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Tanggal tidak valid (cek bulan dan harinya).")


def validate_time(value):
    value = (value or "").strip()
    if not re.fullmatch(r"\d{2}:\d{2}", value):
        raise ValidationError("Format jam harus HH:MM (24 jam), contoh: 23:59.")
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ValidationError("Jam tidak valid (00:00 - 23:59).")


def validate_deadline(date_text, time_text):
    d = validate_date(date_text)
    t = validate_time(time_text)
    return datetime.combine(d, t)


def validate_priority(value):
    value = (value or "").strip().capitalize()
    value = {"Tinggi": "High", "Sedang": "Medium", "Rendah": "Low"}.get(value, value)
    if value not in PRIORITIES:
        raise ValidationError("Prioritas harus Tinggi, Sedang, atau Rendah.")
    return value


def validate_task_id(value):
    try:
        task_id = int(str(value).strip())
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
