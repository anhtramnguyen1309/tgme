import time

from database import sheet
from message_builder import build_rate_message


async def send_daily_rates(application):

    start = time.perf_counter()

    text = build_rate_message()

    if not text:
        print("❌ Không có dữ liệu tỷ giá.")
        return

    # Thêm lời chúc và thông báo
    text += (
        "\n━━━━━━━━━━━━━━\n\n"
        "❤️ <b>Chúc bạn một ngày tốt lành!</b> ❤️\n\n"
        "🤖 <i>Đây là thông báo tự động từ Bot KRW → VND.</i>"
    )

    users = sheet.get_all_users()

    success = 0
    failed = 0
    skipped = 0

    print(f"📤 Bắt đầu gửi tới {len(users)} user...")

    for user in users:

        try:

            uid = int(user["user_id"])
            status = user.get("status", "")
            query = int(user.get("query_count", 0))

            # Trial đã hết lượt
            if status == "trial" and query >= 10:
                skipped += 1
                continue

            # Chỉ gửi cho active và trial
            if status not in ("active", "trial"):
                skipped += 1
                continue

            await application.bot.send_message(
                chat_id=uid,
                text=text,
                parse_mode="HTML",
            )

            success += 1

        except Exception as e:

            failed += 1

            error = str(e)

            print(f"❌ {uid}: {error}")

            # Nếu user đã chặn bot
            if (
                "bot was blocked" in error.lower()
                or "forbidden" in error.lower()
            ):
                try:
                    sheet.change_status(uid, "blocked")
                    print(f"🚫 Đã đánh dấu blocked: {uid}")
                except Exception as ex:
                    print(f"Không thể cập nhật blocked: {ex}")

    elapsed = round(
        time.perf_counter() - start,
        2
    )

    print("\n========== AUTO PUSH ==========")
    print(f"👥 Tổng user   : {len(users)}")
    print(f"✅ Thành công  : {success}")
    print(f"❌ Thất bại    : {failed}")
    print(f"⏭ Bỏ qua      : {skipped}")
    print(f"⏱ Thời gian   : {elapsed} giây")
    print("================================\n")
    from datetime import datetime

    try:

        report = (
        "📊 <b>BÁO CÁO AUTO PUSH</b>\n\n"
        f"👥 Tổng user: <b>{len(users)}</b>\n"
        f"✅ Thành công: <b>{success}</b>\n"
        f"❌ Thất bại: <b>{failed}</b>\n"
        f"⏭ Bỏ qua: <b>{skipped}</b>\n\n"
        f"⏱ Thời gian: <b>{elapsed} giây</b>\n\n"
        f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

        await application.bot.send_message(
        chat_id=1555474257,      # ID Telegram của bạn
        text=report,
        parse_mode="HTML",
    )

    except Exception as e:

         print(f"Lỗi gửi báo cáo admin: {e}")