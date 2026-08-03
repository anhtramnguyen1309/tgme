import requests
import urllib3

urllib3.disable_warnings()

URL = "https://api.sbicosmoney.com:20001/crs/info/country_info"


def get_sbi_rate():
    payload = {
        "countryId": "VIETNAM"
    }

    headers = {
        "User-Agent": "SBICosmoneyApplication/4.7.2",
        "Authorization": "YOUR_AUTHORIZATION",
        "transaction-id": "YOUR_TRANSACTION_ID",
        "transaction-number": "YOUR_TRANSACTION_NUMBER",
        "Accept-Language": "vi",
        "Content-Type": "application/json"
    }

    session = requests.Session()
    session.trust_env = False

    try:
        r = session.post(
            URL,
            json=payload,
            headers=headers,
            verify=False,
            timeout=20
        )

       

        data = r.json()

        if data.get("code") != "200":
            print("API Error:", data)
            return None

        country_list = data.get("data", {}).get("countryList", [])

        for country in country_list:
            if country.get("countryCode") == "VNM":
                rate = float(country["cp1000Amount"]) / 1000
                return round(rate, 3)

        print("Không tìm thấy Việt Nam")
        return None

    except Exception as e:
        print("Lỗi:", e)
        return None


if __name__ == "__main__":
    rate = get_sbi_rate()
    print("SBI:", rate)