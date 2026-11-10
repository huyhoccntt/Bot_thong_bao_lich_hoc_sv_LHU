import os
import sys
import requests
from datetime import datetime
from supabase import create_client

# Cấu hình cố định thông số hệ thống
SUPABASE_URL = "https://sngjjkbmprnngqbtyec.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "sb_secret_t2V5QH5mtUaT5T6bG-XDVA_TyyMSoFl")
LHU_BEARER_TOKEN = os.environ.get("LHU_BEARER_TOKEN", "Bearer VMSH86llrxXyExIVeQG-VU9ky0d7dhDmdqqhTY_N7_A.682AB749407B9020")

# Nhận STUDENT_ID từ tham số dòng lệnh khi gọi script (hoặc dùng mặc định)
if len(sys.argv) > 1:
    STUDENT_ID = sys.argv[1]
else:
    STUDENT_ID = os.environ.get("STUDENT_ID", "125002291")

LHU_API_URL = "https://tapi.lhu.edu.vn/calen/auth/XemLich_LichSinhVien"

def sync_schedule_for_student(student_id):
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Chuẩn hóa định dạng Token
    token = LHU_BEARER_TOKEN if LHU_BEARER_TOKEN.startswith("Bearer ") else f"Bearer {LHU_BEARER_TOKEN}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    
    # Định nghĩa payload gửi đi
    current_date = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "StudentID": student_id,
        "Ngay": current_date,
        "PageIndex": 1,
        "PageSize": 100
    }
    
    try:
        print(f"🔄 Đang đồng bộ lịch học LHU cho Mã Sinh Viên: {student_id}...")
        response = requests.post(LHU_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Xử lý an toàn cấu trúc dữ liệu trả về từ LHU
            schedules = []
            if isinstance(result, list):
                schedules = result
            elif isinstance(result, dict):
                data_field = result.get("data")
                if isinstance(data_field, list):
                    schedules = data_field
                elif isinstance(data_field, dict):
                    schedules = data_field.get("data", [])
                    if not isinstance(schedules, list):
                        schedules = []
            
            if not schedules:
                print(f"📭 Không tìm thấy lịch học nào cho sinh viên {student_id}.")
                return

            print(f"📥 Tìm thấy {len(schedules)} môn học. Đang lưu vào Supabase...")
            for item in schedules:
                if not isinstance(item, dict):
                    continue
                row_data = {
                    "class_code": student_id,
                    "subject_name": item.get("TenMonHoc"),
                    "room": item.get("TenPhong"),
                    "schedule_time": item.get("ThoiGianBD"),
                    "day_of_week": item.get("Thu"),
                    "lecturer": item.get("GiaoVien")
                }
                supabase.table("class_schedules").upsert(row_data).execute()
                
            print(f"✅ Đã đồng bộ thành công lịch học của {student_id} lên Supabase!")
        else:
            print(f"❌ Lỗi API LHU ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi xảy ra: {str(e)}")

if __name__ == "__main__":
    sync_schedule_for_student(STUDENT_ID)