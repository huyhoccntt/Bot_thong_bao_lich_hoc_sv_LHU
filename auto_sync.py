from apscheduler.schedulers.blocking import BlockingScheduler
from main import sync_once

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Ho_Chi_Minh")
    sync_once()  # chạy ngay khi khởi động
    scheduler.add_job(sync_once, "interval", minutes=30, max_instances=1, coalesce=True)
    print("Auto Sync đang chạy: mỗi 30 phút. Nhấn Ctrl+C để dừng.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
