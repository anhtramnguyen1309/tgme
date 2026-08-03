import requests
def get_cross_rate():
    url = "https://crossenf.com/v2/outbound/quote/"

    params = {
        "platform_id": 144,
        "quote_type": "send",
        "sending_amount": 1000000,
        "receiving_amount": "null",
        "use_max_point": False,
        "deposit_type": "Manual",
        "apply_user_limit": 0,
        "is_home": 0,
    }

    session = requests.Session()
    session.trust_env = False

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Cross-OS": "web",
        "Cross-Lang": "en",
        "Cross-User-Agent": "CrossApp",
        "Referer": "https://crossenf.com/remittance",
    }

    r = session.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()

    data = r.json()["data"]

    sending = float(data["sending_amount"])
    receiving = float(data["receiving_amount"])

    # Tiền khuyến mãi cho lần chuyển đầu
    topup = float(data.get("topup_amount", 0))

    # Loại bỏ khuyến mãi
    real_receiving = receiving - topup

    rate = real_receiving / sending

    return round(rate, 3)


if __name__ == "__main__":
    print(get_cross_rate())