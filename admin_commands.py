from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_keyboard
from database import sheet
from config import ADMIN_IDS

# ===== ADMIN STATE =====

ADMIN_STATE = "admin_state"

WAIT_GIAHAN_UID = "wait_giahan_uid"
WAIT_GIAHAN_DAYS = "wait_giahan_days"

WAIT_MOKHOA_UID = "wait_mokhoa_uid"
WAIT_XOA_UID = "wait_xoa_uid"
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
async def process_mokhoa_uid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    # User ID không hợp lệ
    if not text.isdigit():

        clear_state(context)

        await update.message.reply_text(
            "❌ User ID không hợp lệ.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    uid = int(text)

    user = sheet.get_user(uid)

    # Không tìm thấy User
    if not user:

        clear_state(context)

        await update.message.reply_text(
            "❌ Không tìm thấy User.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    sheet.unblock_user(uid)

    clear_state(context)

    await update.message.reply_text(
        f"🔓 Đã mở khóa thành công!\n\n"
        f"👤 {user['name']}\n"
        f"🆔 {uid}",
        reply_markup=get_keyboard(update.effective_user.id),
    )

    try:
        await context.bot.send_message(
            chat_id=uid,
            text=(
                "🎉 Tài khoản của bạn đã được mở khóa.\n\n"
                "Bạn có thể tiếp tục sử dụng bot."
            ),
        )
    except Exception:
        pass
async def start_mokhoa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bạn không có quyền.")
        return

    clear_state(context)
    set_state(context, WAIT_MOKHOA_UID)

    await update.message.reply_text(
        "🔓 MỞ KHÓA TÀI KHOẢN\n\n"
        "🆔 Vui lòng nhập User ID:"
    )
async def start_xoa_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bạn không có quyền.")
        return

    clear_state(context)
    set_state(context, WAIT_XOA_UID)

    await update.message.reply_text(
        "🗑 XÓA USER\n\n"
        "🆔 Vui lòng nhập User ID:"
    )

async def process_xoa_uid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    # User ID không hợp lệ
    if not text.isdigit():

        clear_state(context)

        await update.message.reply_text(
            "❌ User ID không hợp lệ.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    uid = int(text)

    user = sheet.get_user(uid)

    # Không tìm thấy User
    if not user:

        clear_state(context)

        await update.message.reply_text(
            "❌ Không tìm thấy User.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    # Xóa User
    sheet.delete_user(uid)

    clear_state(context)

    await update.message.reply_text(
        f"🗑 Đã xóa User thành công!\n\n"
        f"👤 {user['name']}\n"
        f"🆔 {uid}",
        reply_markup=get_keyboard(update.effective_user.id),
    )

async def start_giahan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bạn không có quyền.")
        return

    clear_state(context)
    set_state(context, WAIT_GIAHAN_UID)

    await update.message.reply_text(
        "📅 GIA HẠN TÀI KHOẢN\n\n"
        "🆔 Vui lòng nhập User ID:"
    )


async def process_giahan_days(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    # Kiểm tra số ngày
    if not text.isdigit():

        clear_state(context)

        await update.message.reply_text(
            "❌ Số ngày không hợp lệ.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    days = int(text)

    if days <= 0:

        clear_state(context)

        await update.message.reply_text(
            "❌ Số ngày phải lớn hơn 0.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    uid = context.user_data.get("uid")

    if not uid:

        clear_state(context)

        await update.message.reply_text(
            "❌ Không tìm thấy User ID.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    # Gia hạn tài khoản
    sheet.extend_days(uid, days)
    sheet.change_status(uid, "active")

    # Lấy thông tin sau khi gia hạn
    user = sheet.get_user(uid)

    # Xóa trạng thái
    clear_state(context)
    context.user_data.pop("uid", None)

    # Thông báo cho admin
    await update.message.reply_text(
        f"✅ Gia hạn thành công!\n\n"
        f"👤 {user['name']}\n"
        f"🆔 ID: {uid}\n"
        f"➕ Đã gia hạn: {days} ngày\n"
        f"📅 HSD mới: {user['expiry']}",
        reply_markup=get_keyboard(update.effective_user.id),
    )

    # Thông báo cho người dùng
    try:
        await context.bot.send_message(
            chat_id=uid,
            text=(
                "🎉 Tài khoản của bạn đã được gia hạn thành công!\n\n"
                f"📅 Thời hạn sử dụng đã được gia hạn thêm {days} ngày.\n\n"
                "❤️ Cảm ơn bạn đã sử dụng dịch vụ!"
            ),
        )
    except Exception:
        # User chưa từng nhắn bot hoặc đã chặn bot
        pass

async def process_giahan_uid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    # User ID không hợp lệ
    if not text.isdigit():

        clear_state(context)

        await update.message.reply_text(
            "❌ User ID không hợp lệ.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    uid = int(text)

    user = sheet.get_user(uid)

    # Không tìm thấy User
    if not user:

        clear_state(context)

        await update.message.reply_text(
            "❌ Không tìm thấy User.\n\n"
            "✅ Thao tác đã được hủy.",
            reply_markup=get_keyboard(update.effective_user.id),
        )
        return

    # Lưu User ID tạm
    context.user_data["uid"] = uid

    set_state(
        context,
        WAIT_GIAHAN_DAYS,
      
    )

    await update.message.reply_text(
        f"👤 {user['name']}\n"
        f"🆔 {uid}\n\n"
        "📅 Nhập số ngày cần gia hạn:"
    )
       
async def log_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not is_admin(update.effective_user.id):

        await update.message.reply_text(
            "⛔ Bạn không có quyền."
        )
        return

    users = sheet.get_all_users()

    if not users:

        await update.message.reply_text(
            "Chưa có dữ liệu."
        )
        return

    text = (
        "📋 <b>DANH SÁCH USER</b>\n\n"
    )

    for user in users:

        status = user["status"]

        if status == "active":
            icon = "🟢"
            expiry = user["expiry"]

        elif status == "trial":
            icon = "🟡"
            expiry = "—"

        elif status == "blocked":
            icon = "⛔"
            expiry = "Bị khóa"

        else:
            icon = "🔴"
            expiry = "Hết hạn"

         
        text += (
            f"{icon} {user['user_id']} - <b>{user['name']}</b>\n"
            f"   📊 {user['query_count']} lần | 🗓️ {expiry}\n\n"
)

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )


async def thongke(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    total = sheet.total_users()
    active = sheet.active_users()
    trial = sheet.trial_users()
    blocked = sheet.blocked_users()
    expired = sheet.expired_users()

    await update.message.reply_text(
        "📊 <b>THỐNG KÊ BOT</b>\n\n"
        f"👥 Tổng User: <b>{total}</b>\n"
        f"✅ Active: <b>{active}</b>\n"
        f"🆓 Trial: <b>{trial}</b>\n"
        f"⛔ Blocked: <b>{blocked}</b>\n"
        f"⌛ Expired: <b>{expired}</b>",
        parse_mode="HTML",
    )