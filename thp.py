import requests


def get_hanpass_rate():
    url = "https://app.hanpass.com/app/v1/remittance/get-cost"

    payload = {
        "inputAmount": "1000000",
        "inputCurrencyCode": "KRW",
        "fromCurrencyCode": "KRW",
        "toCurrencyCode": "VND",
        "toCountryCode": "VN",
        "lang": "ko",
        "memberSeq": "1"
    }

    headers = {
        "origin": "https://www.hanpass.com",
        "referer": "https://www.hanpass.com/",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }

    try:
        session = requests.Session()
        session.trust_env = False

        r = session.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )

        r.raise_for_status()

        data = r.json()

        if data.get("resultCode") != "0":
            return None

  
        exchange_rate = float(data["exchangeRate"])

        # Trừ 1.5 xu
        real_rate = round(exchange_rate - 0.015, 3)

        return real_rate

    except Exception as e:
        print("Hanpass error:", e)
        return None


if __name__ == "__main__":
    rate = get_hanpass_rate()
    print("Hanpass:", rate)