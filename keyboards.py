from telegram import ReplyKeyboardMarkup

from config import ADMIN_IDS


def get_keyboard(user_id: int):

    if user_id in ADMIN_IDS:
        keyboard = [
            ["💱 Tỷ giá"],
            ["💳 Thanh toán", "📅 Hạn sử dụng"],
            ["👤 Log User", "📊 Thống kê"],
            ["🔓 Mở khóa", "📅 Gia hạn"],
            ["🗑 Xóa User"],
        ]
    else:
        keyboard = [
            ["💱 Tỷ giá"],
            ["💳 Thanh toán", "📅 Hạn sử dụng"],
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )