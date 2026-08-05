from keyboards import get_keyboard
from telegram import ReplyKeyboardRemove
from admin_commands import process_giahan_days
from admin_commands import WAIT_GIAHAN_DAYS
from telegram import Update
from telegram.ext import ContextTypes
from admin_commands import get_state
from admin_commands import WAIT_GIAHAN_UID
from admin_commands import process_giahan_uid
from decorators import require_subscription
from message_builder import build_rate_message
from database import sheet
from config import ADMIN_IDS
from admin_commands import (
    start_giahan,
    process_giahan_uid,
    process_giahan_days,

    get_state,
    WAIT_GIAHAN_UID,
    WAIT_GIAHAN_DAYS,

    thongke,
    log_user,
    WAIT_MOKHOA_UID,
    WAIT_XOA_UID,

    start_mokhoa,
    process_mokhoa_uid,

    start_xoa_user,
    process_xoa_uid,
)
ADMIN_STATE = "admin_state"

WAIT_GIAHAN_UID = "wait_giahan_uid"

WAIT_GIAHAN_DAYS = "wait_giahan_days"
def set_state(context, state):
    context.user_data[ADMIN_STATE] = state


def get_state(context):
    return context.user_data.get(ADMIN_STATE)


def clear_state(context):
    context.user_data.pop(ADMIN_STATE, None)


def set_temp(context, key, value):
    context.user_data[key] = value


def get_temp(context, key):
    return context.user_data.get(key)

def is_admin(user_id: int):

    return user_id in ADMIN_IDS


@require_subscription
async def thanhtoan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = (
        "💳 <b>THÔNG TIN THANH TOÁN</b>\n\n"
        "💰 <b>Phí sử dụng:</b> <b>8.999 KRW / Tháng</b>\n\n"
        "🏦 <b>Ngân hàng:</b> Hanabank\n"
        "👤 <b>Chủ tài khoản:</b> LE THI YEN\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔢 <b>SỐ TÀI KHOẢN</b>\n\n"
        "<b>000000055555</b\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📩 Sau khi chuyển khoản thành công,\n"
        "vui lòng nhắn tin đến:\n\n"
        "👉 <b>@JoyceNguyenzz</b>\n\n"
        "⚡ Tài khoản sẽ được kích hoạt ngay sau khi xác nhận thanh toán.\n\n"
        "❤️ Cảm ơn bạn đã tin tưởng và sử dụng dịch vụ!"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )
async def hsd(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    # Nếu user đã bị xóa thì đăng ký lại
    if not sheet.user_exists(user.id):

        sheet.register_user(
            user.id,
            user.full_name,
            user.username or "",
        )

    info = sheet.get_user(user.id)

    if not info:
        await update.message.reply_text(
            "❌ Không tìm thấy tài khoản."
        )
        return

    # ===== Tài khoản dùng thử =====
    if info["status"] == "trial":

        remain = max(10 - int(info["query_count"]), 0)

        text = (
            "📅 THÔNG TIN TÀI KHOẢN\n\n"
            "🆓 Gói: Dùng thử\n"
            f"📊 Lượt dùng thử còn lại: {remain}/10"
        )

    # ===== Tài khoản trả phí =====
    else:

        text = (
            "📅 THÔNG TIN TÀI KHOẢN\n\n"
            "💎 Gói: Trả phí\n"
            f"📅 Hết hạn: {info['expiry']}\n"
            f"📊 Số lần sử dụng: {info['query_count']}"
        )

    await update.message.reply_text(text)
from rate_service import get_cached_rates, update_rates
@require_subscription
async def check_tygia(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    msg = await update.message.reply_text(
        "⏳ Đang lấy tỷ giá, vui lòng chờ (^..^)..."
    )

    try:

        text = build_rate_message()

        if text is None:

            await msg.edit_text(
                "❌ Chưa có dữ liệu tỷ giá.\n"
                "Vui lòng thử lại sau vài giây."
            )
            return

        await msg.edit_text(
            text,
            parse_mode="HTML",
        )

    except Exception as e:

        await msg.edit_text(
            f"❌ Có lỗi xảy ra:\n<code>{e}</code>",
            parse_mode="HTML",
        )

async def process_giahan_days(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "❌ Số ngày không hợp lệ.\n\nNhập lại:"
        )
        return

    days = int(text)

    uid = get_temp(context, "uid")

    # Gia hạn
    sheet.extend_days(uid, days)
    sheet.change_status(uid, "active")

    user = sheet.get_user(uid)

    clear_state(context)
    context.user_data.pop("uid", None)
    # Xóa keyboard cũ
    await update.message.reply_text(
    "✅ Gia hạn thành công!",
    reply_markup=ReplyKeyboardRemove(),
)

# Gửi lại keyboard chính
    await update.message.reply_text(
    f"👤 {user['name']}\n"
    f"🆔 ID: {uid}\n"
    f"➕ Đã gia hạn: {days} ngày\n"
    f"📅 HSD mới: {user['expiry']}",
    reply_markup=get_keyboard(update.effective_user.id),
)

    # Gửi thông báo cho người dùng
    try:
        await context.bot.send_message(
            chat_id=uid,
            text=(
                "🎉 Tài khoản của bạn đã được gia hạn thành công!\n\n"
                f"📅 Thời hạn sử dụng đã được gia hạn thêm {days} ngày.\n\n"
                "Cảm ơn bạn đã sử dụng dịch vụ ❤️"
            ),
        )
    except Exception:
        pass
async def menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    # ==========================
    # XỬ LÝ STATE
    # ==========================

    state = get_state(context)

    if state == WAIT_GIAHAN_UID:
        return await process_giahan_uid(update, context)

    elif state == WAIT_GIAHAN_DAYS:
        return await process_giahan_days(update, context)

    if state == WAIT_MOKHOA_UID:
        return await process_mokhoa_uid(update, context)

    if state == WAIT_XOA_UID:
       return await process_xoa_uid(update, context)

    # ==========================
    # MENU USER
    # ==========================

    if text == "💱 Tỷ giá":
        return await check_tygia(update, context)

    elif text == "💳 Thanh toán":
        return await thanhtoan(update, context)

    elif text == "📅 Hạn sử dụng":
        return await hsd(update, context)

    # ==========================
    # MENU ADMIN
    # ==========================

    elif text == "📅 Gia hạn":
        return await start_giahan(update, context)

    elif text == "🔓 Mở khóa":
     return await start_mokhoa(update, context)

    elif text == "🗑 Xóa User":
     return await start_xoa_user(update, context)
 
    elif text == "📊 Thống kê":
        return await thongke(update, context)

    elif text == "👤 Log User":
        return await log_user(update, context)

    # ==========================
    # KHÔNG NHẬN DIỆN
    # ==========================

    await update.message.reply_text(
        "❓ Chức năng chưa được hỗ trợ."
    )
