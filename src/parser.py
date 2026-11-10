from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import hashlib
import json
import re

TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")
DATE_RE = re.compile(r"(\d{1,2})/(\d{1,2})")


def _week_year(soup, fallback=None):
    text = soup.get_text(" ", strip=True)
    match = re.search(r"Tuần\s+\d+\s*:\s*\d{1,2}/\d{1,2}/(\d{4})", text)
    if match:
        return int(match.group(1))
    return fallback or datetime.now().year


def _date_from_day(day_container, year):
    # Trong snapshot Calen LHU, tiêu đề ngày nằm trong .v-card-title.
    for title in day_container.select(".v-card-title"):
        match = DATE_RE.search(title.get_text(" ", strip=True))
        if match:
            day, month = map(int, match.groups())
            try:
                return datetime(year, month, day).date().isoformat()
            except ValueError:
                return None
    # Fallback: tìm ngày trong phần đầu của thẻ ngày.
    text = day_container.get_text(" ", strip=True)[:100]
    match = DATE_RE.search(text)
    if match:
        day, month = map(int, match.groups())
        try:
            return datetime(year, month, day).date().isoformat()
        except ValueError:
            pass
    return None


def parse_schedule(html_path):
    """Đọc các .lesson-box từ HTML đã lưu trên Calen LHU."""
    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file HTML: {html_path}")

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "lxml")
    year = _week_year(soup)
    schedules = []

    for lesson in soup.select(".lesson-box"):
        # Cấu trúc snapshot: lesson-box -> ... -> thẻ ngày .mb-0.border-t
        day_container = lesson.find_parent("div", class_="mb-0")
        if not day_container:
            continue
        study_date = _date_from_day(day_container, year)
        if not study_date:
            continue

        text = lesson.get_text(" ", strip=True)
        times = TIME_RE.findall(text)
        if len(times) < 2:
            continue
        start_time, end_time = times[0], times[1]

        room = campus = class_code = subject = periods = lesson_type = teacher = None

        location = lesson.select_one(".v-card-text .text-subtitle-1 strong")
        if location:
            room = location.get_text(" ", strip=True)
            campus_span = location.find("span")
            if campus_span:
                campus = campus_span.get_text(" ", strip=True).lstrip("- ").strip() or None
                room = location.get_text(" ", strip=True).replace(campus_span.get_text(" ", strip=True), "").strip(" -")

        for div in lesson.select(".v-card-text div"):
            value = div.get_text(" ", strip=True)
            code_match = re.fullmatch(r"\[?([A-Za-z0-9-]+)\]?", value)
            if code_match:
                class_code = code_match.group(1).strip()
                continue
            subject_match = re.match(r"^(.*?)\s*\(\s*(\d+)T\s*-\s*(.*?)\s*\)$", value)
            if subject_match:
                subject = subject_match.group(1).strip() or None
                periods = f"{subject_match.group(2)}T"
                lesson_type = subject_match.group(3).strip() or None
                continue
            if "color: rgb(40, 79, 158)" in (div.get("style") or ""):
                teacher = value or None

        # Mã định danh ổn định để upsert, không phụ thuộc tên giảng viên.
        identity = "|".join([study_date, start_time, end_time, room or "", class_code or "", subject or ""])
        schedule_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        schedules.append({
            "schedule_id": schedule_id,
            "study_date": study_date,
            "start_time": start_time,
            "end_time": end_time,
            "room": room,
            "campus": campus,
            "class_code": class_code,
            "subject": subject,
            "periods": periods,
            "lesson_type": lesson_type,
            "teacher": teacher,
        })

    # Loại bản ghi trùng nếu HTML có nội dung lặp.
    unique = {item["schedule_id"]: item for item in schedules}
    return sorted(unique.values(), key=lambda x: (x["study_date"], x["start_time"]))


def save_json(schedules, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(schedules, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse lịch học Calen LHU từ HTML")
    parser.add_argument("html", nargs="?", default="data/schedule.html")
    parser.add_argument("--output", default="data/schedule.json")
    args = parser.parse_args()
    result = parse_schedule(args.html)
    save_json(result, args.output)
    print(f"Đã đọc {len(result)} buổi học. JSON: {args.output}")
