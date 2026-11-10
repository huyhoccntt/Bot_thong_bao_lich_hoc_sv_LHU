# LHU Smart Schedule Bot – HTML Parser & Supabase Sync

## 1. Chuẩn bị
- Python 3.10 trở lên.
- Tạo bảng bằng cách chạy `supabase_schema.sql` trong Supabase SQL Editor.
- Sao chép `.env.example` thành `.env`, điền URL, Service Role Key và UUID người dùng.
- Đặt HTML đã tải từ Calen LHU vào `data/schedule.html`.

> Service Role Key chỉ dùng trong backend/local server, tuyệt đối không đưa lên frontend hoặc GitHub. Vì key này có thể bỏ qua RLS, hãy bảo vệ file `.env`.

## 2. Cài thư viện
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Chỉ parse HTML ra JSON (không cần Supabase)
```bash
python -m src.parser data/schedule.html --output data/schedule.json
```

## 4. Parse và đồng bộ Supabase một lần
```bash
python main.py
```

## 5. Tự động chạy mỗi 30 phút
```bash
python auto_sync.py
```

## Giới hạn hiện tại
Đây là đồng bộ định kỳ từ file `data/schedule.html` đã có trên máy. Chương trình chưa tự đăng nhập/tải HTML mới từ Calen LHU. Cần phân tích thêm JavaScript/API hoặc luồng đăng nhập của Calen LHU để bổ sung bước tải lịch mới. Không xóa lịch cũ khi parser không tìm thấy dữ liệu.
