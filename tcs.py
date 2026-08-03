import requests


def get_coinshot_rate():
    try:
        session = requests.Session()
        session.trust_env = False

        # Lấy cookie + CSRF
        session.get(
            "https://coinshot.org/view/calculate?language=vi",
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

        url = "https://coinshot.org/calculate/receiving/i"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://coinshot.org/view/calculate?language=vi",
        }

        data = {
            "receivingCurrency": "VND",
            "sendingCurrency": "KRW",
            "sendingAmount": "1000000"
        }

        response = session.post(
            url,
            headers=headers,
            data=data,
            timeout=10
        )

        response.raise_for_status()

        result = response.json()

        # Tính tỷ giá từ số tiền gửi và số tiền nhận
        sending = float(result["fromAmount"])
        receiving = float(result["toAmount"])

        rate = round(receiving / sending, 3)

        return rate

    except Exception as e:
        print("Coinshot lỗi:", e)
        return None


if __name__ == "__main__":
    rate = get_coinshot_rate()
    print("Coinshot:", rate)