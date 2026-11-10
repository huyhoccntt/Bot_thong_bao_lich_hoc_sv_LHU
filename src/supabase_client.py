import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not url or not key:
    raise RuntimeError("Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong file .env")

supabase = create_client(url, key)
