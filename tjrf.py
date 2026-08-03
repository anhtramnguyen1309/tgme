import requests


def get_jrf_rate():
    url = "https://rateweb.jpremit.co.kr/JrfKorea/GetRate"

    params = {
        "country": "VN",
        "payout": "B",
        "amount": 1000000,
        "currency": "VND",
        "calcby": "C"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://rateweb.jpremit.co.kr/"
    }

    try:
        session = requests.Session()
        session.trust_env = False   # bỏ proxy môi trường

        response = session.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if data["code"] != "0":
            print("JRF API Error:", data)
            return None

        rate = round(float(data["data"]["exchangE_RATE"]), 3)

        return rate

    except Exception as e:
        print("JRF lỗi:", e)
        return None


if __name__ == "__main__":
    rate = get_jrf_rate()
    print("JRF:", rate)

