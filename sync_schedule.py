import os
import requests
from datetime import datetime
from supabase import create_client

# Lấy biến môi trường từ GitHub Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://sngjjkbmprnngqbtyec.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
LHU_BEARER_TOKEN = os.environ.get("LHU_BEARER_TOKEN")
STUDENT_ID = os.environ.get("STUDENT_ID")

LHU_API_URL = "https://tapi.lhu.edu.vn/calen/auth/XemLich_LichSinhVien"

def sync_schedule():
    if not SUPABASE_KEY or not LHU_BEARER_TOKEN or not STUDENT_ID:
        print("❌ Lỗi: Thiếu các biến môi trường cấu hình!")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LHU_BEARER_TOKEN}"
    }
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "StudentID": STUDENT_ID,
        "Ngay": current_date,
        "PageIndex": 1,
        "PageSize": 100
    }
    
    try:
        response = requests.post(LHU_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            schedules = response.json().get("data", {}).get("data", [])
            for item in schedules:
                row_data = {
                    "class_code": STUDENT_ID,
                    "subject_name": item.get("TenMonHoc"),
                    "room": item.get("TenPhong"),
                    "schedule_time": item.get("ThoiGianBD"),
                    "day_of_week": item.get("Thu"),
                    "lecturer": item.get("GiaoVien")
                }
                supabase.table("class_schedules").upsert(row_data).execute()
            print(f"✅ Đã đồng bộ {len(schedules)} môn học từ LHU lên Supabase!")
        else:
            print(f"❌ Lỗi API LHU: {response.status_code}", response.text)
    except Exception as e:
        print("❌ Lỗi xảy ra:", str(e))

if __name__ == "__main__":
    sync_schedule()