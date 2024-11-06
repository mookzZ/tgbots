import os, aiohttp, bs4

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

async def get_data(url: str) -> list[dict]:
    headers = {
        "x-cg-api-key": API_KEY
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(url=url, headers=headers, timeout=10)
        json = await response.json()
        result = []
        for coin in json:
            result.append({
                "id": coin["id"],
                "name": coin["name"]
            })
        return result

async def get_coin(url):
    headers = {
        "x-cg-api-key": API_KEY
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(url=url, headers=headers, timeout=10)
        json = await response.json()
        return json

async def get_joke(category) -> dict:
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=f'https://v2.jokeapi.dev/joke/{category}', timeout=10)
        json = await response.json()
        return json

async def fetch_ebay_links(query):
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = bs4.BeautifulSoup(html, "html.parser")
                items = soup.select("a.s-item__link")
                links = [item['href'] for item in items[:5]]
                print(links)
                return links
            else:
                print(response.status)
                return [response.status, response.text]