import requests


def get_utransfer_rate():
    url = "https://utransfer.com/api/v1/common/fee_calculate"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "devid": "b0f044ce-7a3f-40e8-9113-b97eccd76d5c"
    }

    try:
        session = requests.Session()
        session.trust_env = False   # bỏ proxy môi trường

        response = session.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()["data"]

        for item in data:
            if item["code"] == "VND":

                rate = (
                    item["multiplier"] /
                    item["ex_rate"]
                ) / 100

                return round(rate, 3)

    except Exception as e:
        print(f"UTransfer Error: {e}")

    return None


if __name__ == "__main__":
    rate = get_utransfer_rate()

    if rate:
        print("UTransfer:", rate)
    else:
        print("Không lấy được tỷ giá.")