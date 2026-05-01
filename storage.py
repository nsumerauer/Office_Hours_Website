import os
import sqlite3
from pathlib import Path
from typing import Iterable

from psycopg import connect
from psycopg.rows import dict_row


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
USING_POSTGRES = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")


def _resolve_db_path() -> Path:
    override_path = os.getenv("DATABASE_PATH", "").strip()
    if override_path:
        return Path(override_path)

    if os.getenv("VERCEL"):
        return Path("/tmp/office_hours.db")

    return BASE_DIR / "data" / "office_hours.db"


DB_PATH = _resolve_db_path()


def get_connection():
    if USING_POSTGRES:
        return connect(DATABASE_URL, row_factory=dict_row)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _fetch_all(query: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()
    try:
        with conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _fetch_one(query: str, params: tuple = ()) -> dict | None:
    conn = get_connection()
    try:
        with conn:
            row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _execute(query: str, params: tuple = ()) -> None:
    conn = get_connection()
    try:
        with conn:
            conn.execute(query, params)
    finally:
        conn.close()


def init_db() -> None:
    if USING_POSTGRES:
        _execute(
            """
            CREATE TABLE IF NOT EXISTS student_availability (
                id BIGSERIAL PRIMARY KEY,
                class_code TEXT NOT NULL,
                student_name TEXT NOT NULL,
                day TEXT NOT NULL,
                start_minute INTEGER NOT NULL,
                end_minute INTEGER NOT NULL
            )
            """
        )
        _execute(
            """
            CREATE TABLE IF NOT EXISTS professor_availability (
                id BIGSERIAL PRIMARY KEY,
                class_code TEXT NOT NULL,
                day TEXT NOT NULL,
                start_minute INTEGER NOT NULL,
                end_minute INTEGER NOT NULL
            )
            """
        )
        _execute(
            """
            CREATE TABLE IF NOT EXISTS open_office_hours (
                id BIGSERIAL PRIMARY KEY,
                class_code TEXT NOT NULL,
                day TEXT NOT NULL,
                start_minute INTEGER NOT NULL,
                end_minute INTEGER NOT NULL,
                expected_students INTEGER NOT NULL
            )
            """
        )
        _execute(
            """
            CREATE TABLE IF NOT EXISTS class_settings (
                class_code TEXT PRIMARY KEY,
                weekend_enabled BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        return

    _execute(
        """
        CREATE TABLE IF NOT EXISTS student_availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            student_name TEXT NOT NULL,
            day TEXT NOT NULL,
            start_minute INTEGER NOT NULL,
            end_minute INTEGER NOT NULL
        )
        """
    )
    _execute(
        """
        CREATE TABLE IF NOT EXISTS professor_availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            day TEXT NOT NULL,
            start_minute INTEGER NOT NULL,
            end_minute INTEGER NOT NULL
        )
        """
    )
    _execute(
        """
        CREATE TABLE IF NOT EXISTS open_office_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            day TEXT NOT NULL,
            start_minute INTEGER NOT NULL,
            end_minute INTEGER NOT NULL,
            expected_students INTEGER NOT NULL
        )
        """
    )
    _execute(
        """
        CREATE TABLE IF NOT EXISTS class_settings (
            class_code TEXT PRIMARY KEY,
            weekend_enabled INTEGER NOT NULL DEFAULT 0
        )
        """
    )


def add_student_slot(
    class_code: str, student_name: str, day: str, start_minute: int, end_minute: int
) -> None:
    placeholder = "%s" if USING_POSTGRES else "?"
    _execute(
        f"""
        INSERT INTO student_availability (class_code, student_name, day, start_minute, end_minute)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
        (class_code, student_name, day, start_minute, end_minute),
    )


def remove_student_slot(slot_id: int) -> None:
    placeholder = "%s" if USING_POSTGRES else "?"
    _execute(f"DELETE FROM student_availability WHERE id = {placeholder}", (slot_id,))


def get_student_slots(class_code: str, student_name: str = "") -> list[dict]:
    placeholder = "%s" if USING_POSTGRES else "?"
    if student_name:
        return _fetch_all(
            f"""
            SELECT * FROM student_availability
            WHERE class_code = {placeholder} AND student_name = {placeholder}
            ORDER BY day, start_minute
            """,
            (class_code, student_name),
        )
    return _fetch_all(
        f"""
        SELECT * FROM student_availability
        WHERE class_code = {placeholder}
        ORDER BY day, start_minute
        """,
        (class_code,),
    )


def add_professor_slot(class_code: str, day: str, start_minute: int, end_minute: int) -> None:
    placeholder = "%s" if USING_POSTGRES else "?"
    _execute(
        f"""
        INSERT INTO professor_availability (class_code, day, start_minute, end_minute)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
        (class_code, day, start_minute, end_minute),
    )


def remove_professor_slot(slot_id: int) -> None:
    placeholder = "%s" if USING_POSTGRES else "?"
    _execute(f"DELETE FROM professor_availability WHERE id = {placeholder}", (slot_id,))


def get_professor_slots(class_code: str) -> list[dict]:
    placeholder = "%s" if USING_POSTGRES else "?"
    return _fetch_all(
        f"""
        SELECT * FROM professor_availability
        WHERE class_code = {placeholder}
        ORDER BY day, start_minute
        """,
        (class_code,),
    )


def save_open_slot(
    class_code: str, day: str, start_minute: int, end_minute: int, expected_students: int
) -> None:
    placeholder = "%s" if USING_POSTGRES else "?"
    exists = _fetch_one(
        f"""
        SELECT id FROM open_office_hours
        WHERE class_code = {placeholder} AND day = {placeholder}
          AND start_minute = {placeholder} AND end_minute = {placeholder}
        """,
        (class_code, day, start_minute, end_minute),
    )
    if exists:
        return

    _execute(
        f"""
        INSERT INTO open_office_hours (
            class_code, day, start_minute, end_minute, expected_students
        )
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
        (class_code, day, start_minute, end_minute, expected_students),
    )


def delete_open_slot(slot_id: int) -> None:
    placeholder = "%s" if USING_POSTGRES else "?"
    _execute(f"DELETE FROM open_office_hours WHERE id = {placeholder}", (slot_id,))


def get_open_slots(class_code: str) -> list[dict]:
    placeholder = "%s" if USING_POSTGRES else "?"
    return _fetch_all(
        f"""
        SELECT * FROM open_office_hours
        WHERE class_code = {placeholder}
        ORDER BY day, start_minute
        """,
        (class_code,),
    )


def count_unique_students(class_code: str) -> int:
    placeholder = "%s" if USING_POSTGRES else "?"
    row = _fetch_one(
        f"""
        SELECT COUNT(DISTINCT student_name) AS student_count
        FROM student_availability
        WHERE class_code = {placeholder}
        """,
        (class_code,),
    )
    return int(row["student_count"]) if row else 0


def get_weekend_enabled(class_code: str) -> bool:
    placeholder = "%s" if USING_POSTGRES else "?"
    row = _fetch_one(
        f"""
        SELECT weekend_enabled
        FROM class_settings
        WHERE class_code = {placeholder}
        """,
        (class_code,),
    )
    if not row:
        return False
    return bool(row["weekend_enabled"])


def set_weekend_enabled(class_code: str, enabled: bool) -> None:
    if USING_POSTGRES:
        _execute(
            """
            INSERT INTO class_settings (class_code, weekend_enabled)
            VALUES (%s, %s)
            ON CONFLICT(class_code) DO UPDATE SET weekend_enabled = EXCLUDED.weekend_enabled
            """,
            (class_code, enabled),
        )
        return

    _execute(
        """
        INSERT INTO class_settings (class_code, weekend_enabled)
        VALUES (?, ?)
        ON CONFLICT(class_code) DO UPDATE SET weekend_enabled = excluded.weekend_enabled
        """,
        (class_code, int(enabled)),
    )


def as_dicts(rows: Iterable[dict]) -> list[dict]:
    return [dict(row) for row in rows]
