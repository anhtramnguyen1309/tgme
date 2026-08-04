import asyncio
import inspect
import json
from datetime import datetime

from tcr import get_cross_rate
from te9 import get_e9pay_rate
from tjrf import get_jrf_rate
from thp import get_hanpass_rate
from tgmn import get_gmoney_rate
from tgme import get_gme_rate
from tcs import get_coinshot_rate
from tsbi import get_sbi_rate
from tu import get_utransfer_rate

CACHE_FILE = "rate_cache.json"

rate_cache = {}
last_update = None

# Đọc cache từ file khi khởi động
try:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        rate_cache = data
        last_update = data.get("updated")
except:
    pass

def get_cached_rates():
    return rate_cache

def get_last_update():
    return last_update

async def update_rates():

    apps = {
        "Cross": get_cross_rate,
        "E9Pay": get_e9pay_rate,
        "JRF": get_jrf_rate,
        "Hanpass": get_hanpass_rate,
        "GmoneyTrans": get_gmoney_rate,
        "GME": get_gme_rate,
        "Coinshot": get_coinshot_rate,
        "SBI": get_sbi_rate,
        "Utransfer": get_utransfer_rate
    }

    rates = {}

    for name, func in apps.items():

        try:

            if inspect.iscoroutinefunction(func):
                rate = await func()
            else:
                rate = func()

            if rate is not None:
                rate = round(float(rate), 3)
                rates[name] = rate
                print(f"{name}: {rate}")
            else:
                rates[name] = None
                print(f"{name}: Không có dữ liệu")

        except Exception as e:
            print(f"{name} lỗi: {e}")
            rates[name] = None

    data = {
        from zoneinfo import ZoneInfo

        "updated": datetime.now(
         ZoneInfo("Asia/Seoul")
         ).strftime("%Y-%m-%d %H:%M:%S"),
        "rates": rates,
    }

    # ===== Cache RAM =====
    global rate_cache
    global last_update

    rate_cache = data

    last_update = data["updated"]

    # ===== Backup JSON =====
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("\nĐã cập nhật thành công!")

async def background_updater():

    while True:

        try:
            print("🔄 Đang cập nhật tỷ giá...")

            await update_rates()

            print("✅ Cập nhật thành công")

        except Exception as e:
            print("Lỗi update:", e)

        await asyncio.sleep(60)   # 2 phút
