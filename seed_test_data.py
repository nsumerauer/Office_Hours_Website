from optimizer import optimize_hours
from storage import (
    add_professor_slot,
    add_student_slot,
    as_dicts,
    get_connection,
    get_professor_slots,
    get_student_slots,
    init_db,
    set_weekend_enabled,
)


CLASS_CODE = "1234"


def clear_class_data(class_code: str) -> None:
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM student_availability WHERE class_code = %s" if _is_postgres(conn) else "DELETE FROM student_availability WHERE class_code = ?", (class_code,))
            conn.execute("DELETE FROM professor_availability WHERE class_code = %s" if _is_postgres(conn) else "DELETE FROM professor_availability WHERE class_code = ?", (class_code,))
            conn.execute("DELETE FROM open_office_hours WHERE class_code = %s" if _is_postgres(conn) else "DELETE FROM open_office_hours WHERE class_code = ?", (class_code,))
            conn.execute("DELETE FROM class_settings WHERE class_code = %s" if _is_postgres(conn) else "DELETE FROM class_settings WHERE class_code = ?", (class_code,))
    finally:
        conn.close()


def _is_postgres(conn) -> bool:
    return conn.__class__.__module__.startswith("psycopg")


def seed_students(class_code: str) -> None:
    # M/W/F pattern
    for day in ["Monday", "Wednesday", "Friday"]:
        add_student_slot(class_code, "Alice", day, 600, 720)   # 10:00 - 12:00
        add_student_slot(class_code, "Bob", day, 630, 750)     # 10:30 - 12:30
        add_student_slot(class_code, "Cara", day, 660, 780)    # 11:00 - 13:00

    # T/Th students
    for day in ["Tuesday", "Thursday"]:
        add_student_slot(class_code, "Diego", day, 840, 960)   # 14:00 - 16:00
        add_student_slot(class_code, "Emma", day, 870, 990)    # 14:30 - 16:30

    # Weekend student (useful to test weekend toggle behavior)
    add_student_slot(class_code, "Finn", "Saturday", 660, 780)  # 11:00 - 13:00


def seed_professor(class_code: str) -> None:
    # Professor windows that overlap heavily with M/W/F student blocks
    for day in ["Monday", "Wednesday", "Friday"]:
        add_professor_slot(class_code, day, 600, 840)  # 10:00 - 14:00

    # Lower-overlap T/Th windows
    for day in ["Tuesday", "Thursday"]:
        add_professor_slot(class_code, day, 810, 1020)  # 13:30 - 17:00

    # Weekend window
    add_professor_slot(class_code, "Saturday", 600, 840)  # 10:00 - 14:00


def print_preview(class_code: str) -> None:
    student_slots = as_dicts(get_student_slots(class_code))
    professor_slots = as_dicts(get_professor_slots(class_code))
    recommendations = optimize_hours(student_slots, professor_slots, top_n=5)

    print(f"Seed complete for class code: {class_code}")
    print(f"Student slots: {len(student_slots)}")
    print(f"Professor slots: {len(professor_slots)}")
    print("Top 5 recommended windows:")
    for idx, slot in enumerate(recommendations, start=1):
        start_h, start_m = divmod(slot["start_minute"], 60)
        end_h, end_m = divmod(slot["end_minute"], 60)
        print(
            f"{idx}. {slot['day']} {start_h:02d}:{start_m:02d}-{end_h:02d}:{end_m:02d} | "
            f"Expected students: {slot['score']}"
        )


def seed_demo_class(class_code: str = CLASS_CODE) -> None:
    init_db()
    clear_class_data(class_code)
    set_weekend_enabled(class_code, True)
    seed_students(class_code)
    seed_professor(class_code)


def main() -> None:
    seed_demo_class(CLASS_CODE)
    print_preview(CLASS_CODE)


if __name__ == "__main__":
    main()
