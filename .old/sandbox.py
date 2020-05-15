import aiohttp
import asyncio


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main(url):
    print('start')
    session = aiohttp.ClientSession()
    html = await fetch(session, url)
    print(html[:100])
    await session.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    tasks = []
    for url in ['https://ddragon.leagueoflegends.com/cdn/languages.json',
                'https://ddragon.leagueoflegends.com/api/versions.json',
                'https://ddragon.leagueoflegends.com/cdn/10.9.1/data/en_US/item.json',
                'https://ddragon.leagueoflegends.com/cdn/10.9.1/data/en_US/runesReforged.json',
                'https://ddragon.leagueoflegends.com/cdn/10.9.1/data/en_US/champion.json']:
        task = asyncio.ensure_future(main(url))
        tasks.append(task)

    loop.run_until_complete(asyncio.wait(tasks))

##

