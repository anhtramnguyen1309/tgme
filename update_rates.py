import asyncio
import inspect
import json

from datetime import datetime
from zoneinfo import ZoneInfo
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
        "Utransfer": get_utransfer_rate,
    }

    async def run_one(name, func):
        try:

            if inspect.iscoroutinefunction(func):
                rate = await func()
            else:
                # Chạy hàm đồng bộ trên thread riêng
                rate = await asyncio.to_thread(func)

            if rate is not None:
                rate = round(float(rate), 3)
                print(f"{name}: {rate}")
                return name, rate

            print(f"{name}: Không có dữ liệu")
            return name, None

        except Exception as e:
            print(f"{name} lỗi: {e}")
            return name, None

    # Chạy tất cả cùng lúc
    results = await asyncio.gather(
        *(run_one(name, func) for name, func in apps.items())
    )

    rates = dict(results)

    updated = datetime.now(
        ZoneInfo("Asia/Seoul")
    ).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "updated": updated,
        "rates": rates,
    }

    global rate_cache
    global last_update

    rate_cache = data
    last_update = updated

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("\n✅ Đã cập nhật thành công!")


async def main():

    while True:

        await update_rates()

        print("\nĐợi 5 phút...\n")

        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
