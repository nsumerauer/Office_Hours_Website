from collections import defaultdict


SLOT_MINUTES = 30
SESSION_LENGTH_MINUTES = 60


def minute_range(start_minute: int, end_minute: int, step: int = SLOT_MINUTES) -> list[int]:
    return list(range(start_minute, end_minute, step))


def overlaps(outer_start: int, outer_end: int, inner_start: int, inner_end: int) -> bool:
    return inner_start >= outer_start and inner_end <= outer_end


def optimize_hours(
    student_slots: list[dict], professor_slots: list[dict], top_n: int = 5
) -> list[dict]:
    per_day_student = defaultdict(list)
    for slot in student_slots:
        per_day_student[slot["day"]].append(slot)

    scored_windows: list[dict] = []
    for prof_slot in professor_slots:
        day = prof_slot["day"]
        start = prof_slot["start_minute"]
        end = prof_slot["end_minute"]
        for candidate_start in minute_range(start, end - SESSION_LENGTH_MINUTES + SLOT_MINUTES):
            candidate_end = candidate_start + SESSION_LENGTH_MINUTES
            if candidate_end > end:
                continue

            available_students = set()
            for student_slot in per_day_student.get(day, []):
                if overlaps(
                    student_slot["start_minute"],
                    student_slot["end_minute"],
                    candidate_start,
                    candidate_end,
                ):
                    available_students.add(student_slot["student_name"])

            scored_windows.append(
                {
                    "day": day,
                    "start_minute": candidate_start,
                    "end_minute": candidate_end,
                    "score": len(available_students),
                    "students": sorted(available_students),
                }
            )

    deduped = {}
    for window in scored_windows:
        key = (window["day"], window["start_minute"], window["end_minute"])
        if key not in deduped or window["score"] > deduped[key]["score"]:
            deduped[key] = window

    ranked = sorted(
        deduped.values(),
        key=lambda w: (-w["score"], w["day"], w["start_minute"]),
    )
    return ranked[:top_n]
