import aiohttp
import asyncio
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.ERROR)


async def send_request_through_proxy(url, proxy, semaphore, pbar):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, как Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    async with semaphore:
        session = None
        try:
            session = aiohttp.ClientSession()
            async with session.get(url, proxy=proxy, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    await session.close()
                    return proxy
        except:
            await session.close()
            return None
        finally:
            if session:
                await session.close()
            pbar.update(1)


async def check_proxies(url, proxy_list):
    semaphore = asyncio.Semaphore(3000)
    tasks = []

    with tqdm(total=len(proxy_list), desc=f"Checking proxies for {url.split('//')[-1].split('/')[0]}") as pbar:
        for proxy in proxy_list:
            http_proxy = f'http://{proxy.strip()}'
            tasks.append(send_request_through_proxy(url, http_proxy, semaphore, pbar))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    good_proxies = [proxy.replace('http://', '') for proxy in results if proxy is not None]

    with open('good_proxies.txt', 'w') as f:
        f.write('\n'.join(good_proxies))
    with open('good_proxies.txt') as f:
        read = [i.strip() for i in f.readlines()]
        print(f'Good proxies count: {len(read)} for {url}')


def main_check(site):
    with open('proxies.txt') as proxies_file:
        proxies_list = list(set([proxy.strip().split()[0] for proxy in proxies_file.readlines()]))

    try:
        asyncio.run(check_proxies(site, proxies_list))
    except:
        pass

