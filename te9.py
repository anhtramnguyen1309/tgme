import json
import requests


URL = "https://www.e9pay.co.kr/cmm/calcExchangeRate.do"


PAYLOAD = {
    "DEFRAY_AMOUNT": "1000000",
    "SEND_NATN_COD": "KR",
    "CRNCY_COD": "KRW",
    "RCVER_EXPECT_NATN_COD": "VN03",
    "RCVER_EXPECT_CRNCY_COD": "VND",
    "SIMULATION_YN": "Y",
    "OVSE_FEE_PROMOTION_YN": "N",
    "LANG_COD": ""
}


def get_e9pay_rate():
    try:
        session = requests.Session()
        session.trust_env = False   # bỏ proxy môi trường

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.e9pay.co.kr/",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        r = session.post(
            URL,
            data=PAYLOAD,
            headers=headers,
            timeout=10
        )

        r.raise_for_status()

        data = json.loads(r.json()["data"])

        rate = (
            float(data["RCVER_EXPECT_RECPT_AMOUNT"]) /
            float(data["DEFRAY_AMOUNT"])
        )

        return round(rate, 3)

    except Exception as e:
        print("E9Pay lỗi:", e)
        return None


if __name__ == "__main__":
    rate = get_e9pay_rate()
    print("E9Pay:", rate)