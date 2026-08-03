import re
import httpx


async def get_gmoney_rate():
    url = "https://mapi.gmoneytrans.net/exratenew1/ajx_calcRate.asp"

    params = {
        "receive_amount": "",
        "payout_country": "Viet Nam",
        "total_collected": "1000000",
        "payment_type": "Bank Account",
        "currencyType": "VND",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://mapi.gmoneytrans.net/exratenew1/Default.asp?country=viet%20nam",
        "Origin": "https://mapi.gmoneytrans.net",
    }

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            trust_env=False   # bỏ proxy môi trường
        ) as client:

            response = await client.post(
                url,
                params=params,
                headers=headers
            )

            if response.status_code != 200:
                print("GMoney HTTP Error:", response.status_code)
                return None

            text = response.text

            match = re.search(
                r"exchangeRate--td_clm--([\d.]+)",
                text
            )

            if match:
                return round(float(match.group(1)), 3)

            print("Không tìm thấy exchangeRate")
            return None

    except Exception as e:
        print("GMoney Exception:", e)
        return None


# Test riêng
if __name__ == "__main__":
    import asyncio

    async def main():
        rate = await get_gmoney_rate()
        print("GMoney:", rate)

    asyncio.run(main())