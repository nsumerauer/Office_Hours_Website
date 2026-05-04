from datetime import datetime
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for

from optimizer import optimize_hours
from seed_test_data import seed_demo_class
from storage import (
    add_professor_slot,
    add_student_slot,
    as_dicts,
    count_unique_students,
    delete_open_slot,
    get_open_slots,
    get_professor_slots,
    get_student_slots,
    get_weekend_enabled,
    init_db,
    remove_professor_slot,
    remove_student_slot,
    save_open_slot,
    set_weekend_enabled,
)


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKEND_DAYS = {"Saturday", "Sunday"}
TIME_INCREMENT_MINUTES = 10
DAY_START_MINUTE = 9 * 60
DAY_END_MINUTE = 19 * 60


def parse_time_to_minutes(value: str) -> int:
    dt = datetime.strptime(value, "%H:%M")
    return dt.hour * 60 + dt.minute


def minutes_to_time(value: int) -> str:
    hours = value // 60
    minutes = value % 60
    return f"{hours:02d}:{minutes:02d}"


def build_time_options(step_minutes: int = TIME_INCREMENT_MINUTES) -> list[str]:
    return [minutes_to_time(value) for value in range(DAY_START_MINUTE, DAY_END_MINUTE + 1, step_minutes)]


def normalize_code(value: str) -> str:
    cleaned = value.strip().upper().replace(" ", "")
    return cleaned


def parse_selected_days(form_data) -> list[str]:
    selected_days = [day for day in form_data.getlist("days") if day in DAYS]
    if not selected_days:
        fallback_day = form_data.get("day", "")
        if fallback_day in DAYS:
            selected_days = [fallback_day]
    return selected_days


def filter_weekend_days(days: list[str], weekend_enabled: bool) -> list[str]:
    if weekend_enabled:
        return days
    return [day for day in days if day not in WEEKEND_DAYS]


def times_match_increment(*minutes: int) -> bool:
    return all(value % TIME_INCREMENT_MINUTES == 0 for value in minutes)


def times_within_allowed_range(*minutes: int) -> bool:
    return all(DAY_START_MINUTE <= value <= DAY_END_MINUTE for value in minutes)


app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"
init_db()


@app.context_processor
def helpers():
    return {
        "minutes_to_time": minutes_to_time,
        "days": DAYS,
        "time_options": build_time_options(),
    }


@app.route("/")
def index():
    return redirect(url_for("student_page"))


@app.route("/student")
def student_page():
    class_code = normalize_code(request.args.get("class_code", ""))
    student_name = request.args.get("student_name", "").strip()
    slots = []
    if class_code and student_name:
        slots = as_dicts(get_student_slots(class_code, student_name))
    return render_template(
        "student.html",
        class_code=class_code,
        student_name=student_name,
        slots=slots,
    )


@app.post("/student/add")
def add_student():
    class_code = normalize_code(request.form.get("class_code", ""))
    student_name = request.form.get("student_name", "").strip()
    selected_days = parse_selected_days(request.form)
    start_time = request.form.get("start_time", "")
    end_time = request.form.get("end_time", "")

    if not class_code:
        class_code = f"CLASS-{uuid4().hex[:6].upper()}"
        flash(f"No class code entered. Generated code: {class_code}", "info")

    if not student_name or not selected_days or not start_time or not end_time:
        flash("Please complete all fields for class times.", "error")
        return redirect(url_for("student_page", class_code=class_code, student_name=student_name))

    start_minute = parse_time_to_minutes(start_time)
    end_minute = parse_time_to_minutes(end_time)
    if not times_within_allowed_range(start_minute, end_minute):
        flash("Times must be between 09:00 and 19:00.", "error")
        return redirect(url_for("student_page", class_code=class_code, student_name=student_name))
    if not times_match_increment(start_minute, end_minute):
        flash("Times must be in 10-minute increments.", "error")
        return redirect(url_for("student_page", class_code=class_code, student_name=student_name))
    if end_minute <= start_minute:
        flash("End time must be after start time.", "error")
        return redirect(url_for("student_page", class_code=class_code, student_name=student_name))

    for day in selected_days:
        add_student_slot(class_code, student_name, day, start_minute, end_minute)
    flash(f"Class time added for {len(selected_days)} day(s).", "success")
    return redirect(url_for("student_page", class_code=class_code, student_name=student_name))


@app.post("/student/remove")
def remove_student():
    class_code = normalize_code(request.form.get("class_code", ""))
    student_name = request.form.get("student_name", "").strip()
    slot_id = int(request.form.get("slot_id", "0"))
    remove_student_slot(slot_id)
    flash("Class time removed.", "success")
    return redirect(url_for("student_page", class_code=class_code, student_name=student_name))


@app.route("/professor")
def professor_page():
    class_code = normalize_code(request.args.get("class_code", ""))
    professor_slots = as_dicts(get_professor_slots(class_code)) if class_code else []
    open_slots = as_dicts(get_open_slots(class_code)) if class_code else []
    student_count = count_unique_students(class_code) if class_code else 0
    weekend_enabled = get_weekend_enabled(class_code) if class_code else False
    if not weekend_enabled:
        professor_slots = [slot for slot in professor_slots if slot["day"] not in WEEKEND_DAYS]
        open_slots = [slot for slot in open_slots if slot["day"] not in WEEKEND_DAYS]
    return render_template(
        "professor.html",
        class_code=class_code,
        professor_slots=professor_slots,
        open_slots=open_slots,
        student_count=student_count,
        weekend_enabled=weekend_enabled,
        recommendations=[],
        selected_day="",
    )


@app.post("/professor/add-availability")
def add_professor_availability():
    class_code = normalize_code(request.form.get("class_code", ""))
    selected_days = parse_selected_days(request.form)
    start_time = request.form.get("start_time", "")
    end_time = request.form.get("end_time", "")

    if not class_code:
        flash("Class code is required.", "error")
        return redirect(url_for("professor_page"))

    if not selected_days or not start_time or not end_time:
        flash("Please complete all professor availability fields.", "error")
        return redirect(url_for("professor_page", class_code=class_code))
    weekend_enabled = get_weekend_enabled(class_code)
    filtered_days = filter_weekend_days(selected_days, weekend_enabled)
    if not filtered_days:
        flash("Weekend is disabled for this class. Select weekday(s) or enable weekend hours.", "error")
        return redirect(url_for("professor_page", class_code=class_code))

    start_minute = parse_time_to_minutes(start_time)
    end_minute = parse_time_to_minutes(end_time)
    if not times_within_allowed_range(start_minute, end_minute):
        flash("Times must be between 09:00 and 19:00.", "error")
        return redirect(url_for("professor_page", class_code=class_code))
    if not times_match_increment(start_minute, end_minute):
        flash("Times must be in 10-minute increments.", "error")
        return redirect(url_for("professor_page", class_code=class_code))
    if end_minute <= start_minute:
        flash("End time must be after start time.", "error")
        return redirect(url_for("professor_page", class_code=class_code))

    for day in filtered_days:
        add_professor_slot(class_code, day, start_minute, end_minute)
    if len(filtered_days) != len(selected_days):
        flash("Weekend was off, so only weekday availability was added.", "info")
    flash(f"Professor availability added for {len(filtered_days)} day(s).", "success")
    return redirect(url_for("professor_page", class_code=class_code))


@app.post("/professor/remove-availability")
def remove_professor_availability():
    class_code = normalize_code(request.form.get("class_code", ""))
    slot_id = int(request.form.get("slot_id", "0"))
    remove_professor_slot(slot_id)
    flash("Professor availability removed.", "success")
    return redirect(url_for("professor_page", class_code=class_code))


@app.post("/professor/optimize")
def professor_optimize():
    class_code = normalize_code(request.form.get("class_code", ""))
    selected_day = request.form.get("selected_day", "").strip()
    if not class_code:
        flash("Class code is required for optimization.", "error")
        return redirect(url_for("professor_page"))
    if selected_day and selected_day not in DAYS:
        flash("Please choose a valid day filter.", "error")
        return redirect(url_for("professor_page", class_code=class_code))

    student_slots = as_dicts(get_student_slots(class_code))
    professor_slots = as_dicts(get_professor_slots(class_code))
    open_slots = as_dicts(get_open_slots(class_code))
    student_count = count_unique_students(class_code)
    weekend_enabled = get_weekend_enabled(class_code)
    if not weekend_enabled:
        student_slots = [slot for slot in student_slots if slot["day"] not in WEEKEND_DAYS]
        professor_slots = [slot for slot in professor_slots if slot["day"] not in WEEKEND_DAYS]
        open_slots = [slot for slot in open_slots if slot["day"] not in WEEKEND_DAYS]
    if selected_day and not weekend_enabled and selected_day in WEEKEND_DAYS:
        flash("Weekend is disabled for this class. Choose a weekday filter.", "error")
        return redirect(url_for("professor_page", class_code=class_code))
    if selected_day:
        student_slots = [slot for slot in student_slots if slot["day"] == selected_day]
        professor_slots = [slot for slot in professor_slots if slot["day"] == selected_day]
    recommendations = optimize_hours(student_slots, professor_slots, top_n=8)
    if not recommendations:
        flash("No recommendation windows found. Add more class times or professor availability.", "info")

    return render_template(
        "professor.html",
        class_code=class_code,
        professor_slots=professor_slots,
        open_slots=open_slots,
        student_count=student_count,
        weekend_enabled=weekend_enabled,
        recommendations=recommendations,
        selected_day=selected_day,
    )


@app.post("/professor/weekend-setting")
def update_weekend_setting():
    class_code = normalize_code(request.form.get("class_code", ""))
    if not class_code:
        flash("Class code is required to update weekend settings.", "error")
        return redirect(url_for("professor_page"))

    enabled = request.form.get("weekend_enabled") == "on"
    set_weekend_enabled(class_code, enabled)
    if enabled:
        flash("Weekend office hours are now enabled.", "success")
    else:
        flash("Weekend office hours are now disabled.", "success")
    return redirect(url_for("professor_page", class_code=class_code))


@app.post("/professor/load-demo")
def load_demo_data():
    class_code = "1234"
    seed_demo_class(class_code)
    flash("Demo data loaded for class code 1234. You can now test optimization.", "success")
    return redirect(url_for("professor_page", class_code=class_code))


@app.post("/professor/open")
def add_open_hour():
    class_code = normalize_code(request.form.get("class_code", ""))
    day = request.form.get("day", "")
    start_minute = int(request.form.get("start_minute", "0"))
    end_minute = int(request.form.get("end_minute", "0"))
    expected_students = int(request.form.get("score", "0"))
    save_open_slot(class_code, day, start_minute, end_minute, expected_students)
    flash("Office hour opened.", "success")
    return redirect(url_for("professor_page", class_code=class_code))


@app.post("/professor/remove-open")
def remove_open_hour():
    class_code = normalize_code(request.form.get("class_code", ""))
    slot_id = int(request.form.get("slot_id", "0"))
    delete_open_slot(slot_id)
    flash("Opened office-hour time removed.", "success")
    return redirect(url_for("professor_page", class_code=class_code))


if __name__ == "__main__":
    app.run(debug=True)
