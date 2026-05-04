from optimizer import optimize_hours


def test_optimize_hours_ranks_highest_students_free_from_class_first():
    student_slots = [
        {"day": "Monday", "student_name": "A", "start_minute": 600, "end_minute": 720},
        {"day": "Monday", "student_name": "B", "start_minute": 630, "end_minute": 750},
        {"day": "Monday", "student_name": "C", "start_minute": 660, "end_minute": 780},
    ]
    professor_slots = [{"day": "Monday", "start_minute": 600, "end_minute": 840}]

    results = optimize_hours(student_slots, professor_slots, top_n=3)

    assert len(results) == 3
    assert results[0]["day"] == "Monday"
    assert results[0]["start_minute"] == 780
    assert results[0]["end_minute"] == 840
    assert results[0]["score"] == 3


def test_optimize_hours_returns_empty_when_no_professor_data():
    student_slots = [{"day": "Monday", "student_name": "A", "start_minute": 600, "end_minute": 720}]
    professor_slots = []

    assert optimize_hours(student_slots, professor_slots, top_n=5) == []
