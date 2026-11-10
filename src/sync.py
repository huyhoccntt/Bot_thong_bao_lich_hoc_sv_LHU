import os
from dotenv import load_dotenv
from src.supabase_client import supabase

load_dotenv()
USER_ID = os.getenv("SUPABASE_USER_ID")


def save_schedules(schedules):
    if not USER_ID:
        raise RuntimeError("Thiếu SUPABASE_USER_ID trong file .env")
    if not schedules:
        print("Không có buổi học để đồng bộ; không thay đổi dữ liệu trên Supabase.")
        return []

    rows = [{**item, "user_id": USER_ID} for item in schedules]
    response = supabase.table("class_schedules").upsert(
        rows, on_conflict="user_id,schedule_id"
    ).execute()
    print(f"Đã đồng bộ {len(response.data or [])} bản ghi lên Supabase.")
    return response.data or []
