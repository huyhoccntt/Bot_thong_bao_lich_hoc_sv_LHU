from pathlib import Path
from src.parser import parse_schedule, save_json
from src.sync import save_schedules

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "data" / "schedule.html"
JSON_FILE = BASE_DIR / "data" / "schedule.json"


def sync_once():
    print("Đang đọc lịch từ HTML...")
    schedules = parse_schedule(HTML_FILE)
    if not schedules:
        raise RuntimeError("Parser không tìm thấy buổi học nào. Kiểm tra file HTML hoặc cấu trúc trang.")
    save_json(schedules, JSON_FILE)
    print(f"Đã xuất JSON: {JSON_FILE} ({len(schedules)} buổi)")
    save_schedules(schedules)


if __name__ == "__main__":
    sync_once()
