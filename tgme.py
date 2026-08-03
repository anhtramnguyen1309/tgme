import httpx


async def get_gme_rate():
    url = "https://online.gmeremit.com/ExchangeRate.aspx"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://online.gmeremit.com/ExchangeRate.aspx?width=auto",
        "X-Requested-With": "XMLHttpRequest",
    }

    payload = {
        "method": "GetExRate",
        "pCurr": "VND",
        "pCountryName": "Vietnam",
        "collCurr": "KRW",
        "deliveryMethod": "2",
        "cAmt": "5000000",
        "pAmt": "",
        "cardOnline": "false",
        "calBy": "C",
    }

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            trust_env=False   # bỏ proxy môi trường
        ) as client:

            response = await client.post(
                url,
                data=payload,
                headers=headers
            )

            if response.status_code != 200:
                print(f"GME HTTP Error: {response.status_code}")
                return None

            data = response.json()

            if data.get("errorCode") != "0":
                print("GME API Error:", data)
                return None

            return round(float(data["exRate"]), 3)

    except Exception as e:
        print("GME Exception:", e)
        return None


# test riêng
if __name__ == "__main__":
    import asyncio

    async def main():
        rate = await get_gme_rate()
        print("GME:", rate)

    asyncio.run(main())