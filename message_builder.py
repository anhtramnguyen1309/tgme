from rate_service import get_cached_rates


def build_rate_message(is_push=False):

    cache = get_cached_rates()

    if not cache:
        return None

    updated = cache.get("updated", "Không rõ")
    data = cache.get("rates", {})

    rates = [
        ("SBI", data.get("SBI")),
        ("JRF", data.get("JRF")),
        ("Hanpass", data.get("Hanpass")),
        ("GME", data.get("GME")),
        ("Gmoney", data.get("GmoneyTrans")),
        ("Cross", data.get("Cross")),
        ("Coinshot", data.get("Coinshot")),
        ("Utransfer", data.get("Utransfer")),
        ("E9", data.get("E9Pay")),
    ]

    valid_rates = [
        (name, rate)
        for name, rate in rates
        if rate is not None
    ]

    if not valid_rates:
        return None

    valid_rates.sort(
        key=lambda x: x[1],
        reverse=True,
    )

    if is_push:

        text = (
            "🔔 <b>THÔNG BÁO TỶ GIÁ KRW → VND</b>\n\n"
            f"🕒 <b>Cập nhật:</b> <code>{updated}</code>\n"
            "━━━━━━━━━━━━━━\n\n"
        )

    else:

        text = (
            "🇰🇷💸 <b>TỶ GIÁ CHUYỂN TIỀN KRW → VND</b>\n\n"
            f"🕒 <b>Cập nhật:</b> <code>{updated}</code>\n"
            "━━━━━━━━━━━━━━\n\n"
            "🏆 <b>TOP TỶ GIÁ</b>\n\n"
        )

    medals = ["🥇", "🥈", "🥉"]

    for i, (name, rate) in enumerate(valid_rates):

        icon = medals[i] if i < 3 else "🏦"

        text += (
            f"{icon} <b>{name}</b>: "
            f"<code>{rate:.3f}</code>\n"
        )

    if is_push:

        text += (
            "\n━━━━━━━━━━━━━━\n"
            "Chúc bạn một ngày tốt lành❤️\n"
            "💡 Đây là thông báo tự động từ Bot KRW → VND."
            
        )

    return text