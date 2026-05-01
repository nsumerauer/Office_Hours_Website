def test_student_add_multi_day_creates_multiple_slots(client, configured_modules):
    storage = configured_modules["storage"]

    response = client.post(
        "/student/add",
        data={
            "class_code": "ABC1",
            "student_name": "Test Student",
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "10:00",
            "end_time": "11:00",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    slots = storage.get_student_slots("ABC1", "Test Student")
    assert len(slots) == 3
    assert {slot["day"] for slot in slots} == {"Monday", "Wednesday", "Friday"}


def test_professor_weekend_off_blocks_weekend_availability(client, configured_modules):
    storage = configured_modules["storage"]
    class_code = "WEEK0"

    storage.set_weekend_enabled(class_code, False)

    response = client.post(
        "/professor/add-availability",
        data={
            "class_code": class_code,
            "days": ["Saturday", "Sunday"],
            "start_time": "10:00",
            "end_time": "11:00",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    slots = storage.get_professor_slots(class_code)
    assert len(slots) == 0


def test_professor_load_demo_data_populates_class_1234(client, configured_modules):
    storage = configured_modules["storage"]

    response = client.post("/professor/load-demo", follow_redirects=True)

    assert response.status_code == 200
    assert b"class code 1234" in response.data.lower()
    assert len(storage.get_student_slots("1234")) > 0
    assert len(storage.get_professor_slots("1234")) > 0
