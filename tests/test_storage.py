def test_save_open_slot_deduplicates_entries(configured_modules):
    storage = configured_modules["storage"]
    class_code = "T100"

    storage.init_db()
    storage.save_open_slot(class_code, "Monday", 600, 660, 2)
    storage.save_open_slot(class_code, "Monday", 600, 660, 2)

    open_slots = storage.get_open_slots(class_code)
    assert len(open_slots) == 1


def test_weekend_setting_roundtrip(configured_modules):
    storage = configured_modules["storage"]
    class_code = "T200"

    assert storage.get_weekend_enabled(class_code) is False
    storage.set_weekend_enabled(class_code, True)
    assert storage.get_weekend_enabled(class_code) is True
    storage.set_weekend_enabled(class_code, False)
    assert storage.get_weekend_enabled(class_code) is False
