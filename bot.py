from apscheduler.schedulers.asyncio import AsyncIOScheduler
from push_service import send_daily_rates
from admin_commands import *
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from rate_service import background_updater
from config import BOT_TOKEN
from keyboards import get_keyboard
import asyncio
from commands import (
    check_tygia,
    thanhtoan,
    hsd,
    menu_handler,
)

from admin_commands import (
    log_user,
    thongke,

    start_giahan,

    start_mokhoa,
    process_mokhoa_uid,

    start_xoa_user,
    process_xoa_uid,
)
# ==========================================
# START
# ==========================================
from push_service import send_daily_rates
async def test_push(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    # Chỉ admin được test
    if update.effective_user.id not in ADMIN_IDS:

        await update.message.reply_text(
            "⛔ Bạn không có quyền."
        )
        return

    await update.message.reply_text(
        "📤 Đang gửi thử thông báo..."
    )

    await send_daily_rates(
        context.application
    )

    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    await update.message.reply_text(
        "👋 Chào mừng bạn đến với Bot KRW → VND\n\n"
        "Vui lòng chọn chức năng bên dưới (^.^)",
        reply_markup=get_keyboard(user.id)
    )


scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def post_init(application):

    # background updater
    asyncio.create_task(background_updater())

    # Auto Push 10h
    scheduler.add_job(
        send_daily_rates,
        "cron",
        hour=10,
        minute=0,
        args=[application],
    )

    # 14h
    scheduler.add_job(
        send_daily_rates,
        "cron",
        hour=14,
        minute=0,
        args=[application],
    )

    # 18h
    scheduler.add_job(
        send_daily_rates,
        "cron",
        hour=18,
        minute=0,
        args=[application],
    )

    scheduler.start()
    print("✅ Scheduler started")
def main():
    application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(post_init)
    .build()
)
    
    # ===========================
    # USER COMMAND
    # ===========================

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("tygia", check_tygia)
    )

    application.add_handler(
        CommandHandler("thanhtoan", thanhtoan)
    )

    application.add_handler(
        CommandHandler("hsd", hsd)
    )

    # ===========================
    # ADMIN COMMAND
    # ===========================

    application.add_handler(
        CommandHandler("log_user", log_user)
    )

    application.add_handler(
        CommandHandler("thongke", thongke)
    )

    application.add_handler(
        CommandHandler("mokhoa",start_mokhoa)
    )

    application.add_handler(
        CommandHandler("giahan", start_giahan)
    )

    application.add_handler(
        CommandHandler("xoa_user", start_xoa_user)
    )

    application.add_handler(
    CommandHandler(
        "test_push",
        test_push,
    )
)   
    
    # ===========================
    # MENU BUTTON
    # ===========================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu_handler,
        )
    )
 
    
    print("✅ Bot KRW-VND đang chạy...")

    application.run_polling()

    
if __name__ == "__main__":
    main()
