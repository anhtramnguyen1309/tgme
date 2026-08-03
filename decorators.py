from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from database import sheet
import time
import asyncio

def save_user_data_sync(user_id, command):

    info = sheet.get_user(user_id)

    if not info:
        return

    # Tăng số lượt sử dụng
    sheet.increase_query(user_id)

    # Cập nhật lệnh cuối
    sheet.update_last_query(
        user_id,
        command,
    )

    # Ghi log
    sheet.write_log(
        user_id,
        command,
    )

def require_subscription(func):

    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs,
    ):

        user = update.effective_user

        # ==========================
        # Đăng ký nếu chưa có
        # ==========================
        if not sheet.user_exists(user.id):

            sheet.register_user(
                user.id,
                user.full_name,
                user.username or "",
            )

        info = sheet.get_user(user.id)

        # ==========================
        # Kiểm tra quyền sử dụng
        # ==========================
        if not sheet.can_use(user.id):

            if info["status"] == "trial":

                await update.message.reply_text(
                    "🚫 Bạn đã sử dụng hết 10 lượt dùng thử.\n\n"
                    "💳 Vui lòng nhấn '💳 Thanh toán' để tiếp tục sử dụng dịch vụ.\n\n"
                    "Xin cảm ơn ❤️"
                )

            else:

                await update.message.reply_text(
                    "❌ Gói sử dụng đã hết hạn.\n\n"
                    "💳 Vui lòng gia hạn để tiếp tục sử dụng dịch vụ."
                )

            return

        # ==========================
        # Thực hiện lệnh trước
        # ==========================
        result = await func(
            update,
            context,
            *args,
            **kwargs,
        )

        # ==========================
        # Ghi Google Sheet chạy nền
        # ==========================
        asyncio.create_task(
            asyncio.to_thread(
                save_user_data_sync,
                user.id,
                update.message.text,
            )
        )

        return result

    return wrapper