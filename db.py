"""
db.py — طبقة قاعدة البيانات الدائمة، بدون أي حساب خارجي أو مفاتيح API.

يستخدم SQLite (ملف واحد داخل مجلد المشروع نفسه) بدل خدمة خارجية —
أبسط بكثير: صفر تسجيل حساب، صفر مفاتيح، صفر إعدادات Secrets.

ملاحظة: البيانات تبقى محفوظة طول ما التطبيق نشِط ومُستخدم، لكن لو
أعيد نشر المشروع من جديد أو نام لفترة طويلة جدًا، قد يبدأ الملف من
جديد. للعروض التقديمية والمسابقات هذا كافٍ تمامًا — ارفعوا الأرشيف
المرجعي قريبًا من موعد العرض.
"""

import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS enf_archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            captured_at TEXT NOT NULL,
            freq_hz REAL NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_captured_at ON enf_archive (captured_at)")
    conn.commit()
    return conn


def save_reference_points(start_time: datetime.datetime, rel_times, freqs):
    """يحفظ نقاط الأرشيف بالوقت الحقيقي (start_time + الزمن النسبي لكل نقطة)."""
    conn = _get_conn()
    rows = [
        ((start_time + datetime.timedelta(seconds=float(rt))).isoformat(), float(f))
        for rt, f in zip(rel_times, freqs)
    ]
    conn.executemany("INSERT INTO enf_archive (captured_at, freq_hz) VALUES (?, ?)", rows)
    conn.commit()
    conn.close()
    return len(rows)


def load_reference_archive():
    """يحمّل الأرشيف الكامل مرتّبًا زمنيًا: (قائمة أوقات حقيقية، قائمة ترددات)."""
    conn = _get_conn()
    cur = conn.execute("SELECT captured_at, freq_hz FROM enf_archive ORDER BY captured_at")
    data = cur.fetchall()
    conn.close()
    times = [datetime.datetime.fromisoformat(r[0]) for r in data]
    freqs = [r[1] for r in data]
    return times, freqs


def archive_count():
    conn = _get_conn()
    cur = conn.execute("SELECT COUNT(*) FROM enf_archive")
    n = cur.fetchone()[0]
    conn.close()
    return n


def archive_time_range():
    times, _ = load_reference_archive()
    if not times:
        return None, None
    return min(times), max(times)
