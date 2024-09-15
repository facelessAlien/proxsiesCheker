import base64
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_valid_ip(ip_addr) -> bool:
    import ipaddress
    try:
        ipaddress.ip_address(ip_addr)
        return True
    except:
        return False


def fetch_proxies():
    proxies_collections = {}
    failed_request = []

    print('download proxies...')
    print(f'{"=" * 50}')

    def fetch_sslproxies():
        try:
            url = 'https://www.sslproxies.org/'
            headers = {'User-Agent': UserAgent().random}
            response = requests.get(url=url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            proxy_text = soup.find('textarea', class_='form-control').text
            proxies_collections['sslproxies'] = set(proxy_text.split()[9:])
            print(f'[+] sslproxies {len(proxies_collections.get("sslproxies"))}')
        except:
            print(f'[-] sslproxies')
            failed_request.append('https://www.sslproxies.org/')

    def fetch_advanced_name():
        try:
            url = 'https://advanced.name/ru/freeproxy?type=https'
            headers = {'User-Agent': UserAgent().random}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            rows = soup.find_all('tr')[1:]

            proxies = []
            for row in rows:
                ip_encoded = row.find('td', {'data-ip': True})
                port_encoded = row.find('td', {'data-port': True})

                if ip_encoded and port_encoded:
                    ip = base64.b64decode(ip_encoded['data-ip']).decode('utf-8')
                    port = base64.b64decode(port_encoded['data-port']).decode('utf-8')
                    proxies.append(f"{ip}:{port}")
            proxies_collections['advanced.name'] = proxies
            print(f'[+] advanced.name {len(proxies_collections.get("advanced.name"))}')
        except:
            print(f'[-] advanced.name')
            failed_request.append('https://advanced.name/')

    def fetch_github():
        try:
            url = 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
            response = requests.get(url=url, timeout=10)
            proxies_collections['github'] = set(response.text.strip().split())
            print(f'[+] github {len(proxies_collections.get("github"))}')
        except:
            print(f'[-] github')
            failed_request.append('https://raw.githubusercontent.com/')

    def fetch_proxy_list():
        try:
            decoded_strings = set()
            for page in range(1, 3):
                url = f'http://proxy-list.org/russian/search.php?search=ssl-yes&country=any&type=any&port=any&ssl=yes&p={page}'
                response = requests.get(url, timeout=10)
                pattern = re.compile(r"Proxy\('([^']+)'\)")
                encoded_strings = pattern.findall(response.text)
                decoded_strings.update([base64.b64decode(s).decode('utf-8') for s in encoded_strings])
            proxies_collections['proxy-list'] = decoded_strings
            print(f'[+] proxy-list {len(proxies_collections.get("proxy-list"))}')
        except:
            print(f'[-] proxy-list')
            failed_request.append('http://proxy-list.org/')

    def fetch_geonode():
        try:
            geonode = []
            url = 'https://proxylist.geonode.com/api/proxy-list?protocols=http&limit=500&page=1&sort_by=lastChecked&sort_type=desc'
            r = requests.get(url, timeout=10).json()
            ip_port = [f"{i.get('ip')}:{i.get('port')}" for i in r.get('data')]
            for i in ip_port:
                geonode.append(i)
            proxies_collections['geonode'] = geonode
            print(f'[+] geonode {len(proxies_collections.get("geonode"))}')
        except:
            print(f'[-] geonode')
            failed_request.append('https://proxylist.geonode.com/')

    def fetch_proxyscrape():
        try:
            url = 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&skip=0&proxy_format=protocolipport&format=json&limit=2000'
            r = requests.get(url, timeout=10).json()
            proxyscrape = []
            for i in r.get('proxies'):
                if i.get('ssl') is True:
                    proxyscrape.append(f"{i.get('ip')}:{i.get('port')}")
            proxies_collections['proxyscrape'] = proxyscrape
            print(f'[+] proxyscrape {len(proxies_collections.get("proxyscrape"))}')
        except:
            print(f'[-] proxyscrape')
            failed_request.append('https://api.proxyscrape.com/')

    def fetch_spys():
        try:
            url = 'https://spys.me/proxy.txt'
            r = requests.get(url, timeout=10).text
            pattern = re.compile(r'\d+\.\d+\.\d+\.\d+:\d+')
            proxies = pattern.findall(r)
            proxies_collections['spys'] = proxies
            print(f'[+] spys {len(proxies_collections.get("spys"))}')
        except:
            print(f'[-] spys')
            failed_request.append('https://spys.me/')

    def fetch_geoxy():
        try:
            session = requests.Session()
            url = 'https://gologin.com/ru/free-proxy/'
            session.headers.update({'User-Agent': UserAgent().random})
            response = session.get(url, timeout=10)
            html_content = response.text

            auth_pattern = re.compile(r"Authorization':\s*'([^']+)'")
            match = auth_pattern.search(html_content)

            if match:
                auth_token = match.group(1)
                url = 'https://geoxy.io/proxies?count=99999'
                session.headers.update({
                    'Authorization': auth_token,
                    'Content-Type': 'application/json'
                })
                response = session.get(url)
                res_dict = response.json()

                ip_addresses = [item['address'] for item in res_dict]
                proxies_collections['geoxy'] = ip_addresses
                print(f'[+] geoxy {len(proxies_collections.get("geoxy"))}')
        except:
            print(f'[-] geoxy')
            failed_request.append('https://gologin.com/ru/free-proxy/')

    def fetch_fineproxy():
        try:
            url = 'https://fineproxy.org/wp-content/themes/fineproxyorg/proxy-list.php?0.8017879570332158'
            headers = {
                'Priority': 'u=1, i',
                'Referer': 'https://fineproxy.org/free-proxy/',
                'User-Agent': UserAgent().random
            }
            r = requests.get(url, headers=headers, timeout=10)
            res = r.json()
            ip_port = [i.get('host') + ':' + i.get('port') for i in res if i.get('http') == '1' and i.get('host')[0].isdigit()]
            proxies_collections['fineproxy'] = [ip_addr for ip_addr in ip_port if is_valid_ip(ip_addr.split(':')[0])]
            print(f'[+] fineproxy {len(proxies_collections.get("fineproxy"))}')
        except:
            print(f'[-] fineproxy')
            failed_request.append('https://fineproxy.org/')

    def fetch_spaceproxy():
        try:
            url = 'https://api.proxy-checker.net/api/free-proxy-list/'
            headers = {
                'User-Agent': UserAgent().random
            }
            r = requests.get(url, headers=headers, timeout=10)
            res = r.json()
            spaceproxy = []
            for row in res:
                protocol = row.get('protocol')
                if protocol == 'http':
                    proxy = row.get('ip') + ':' + str(row.get('port'))
                    spaceproxy.append(proxy)
            proxies_collections['spaceproxy'] = spaceproxy
            print(f'[+] spaceproxy {len(proxies_collections.get("spaceproxy"))}')
        except:
            print(f'[-] spaceproxy')
            failed_request.append('https://api.proxy-checker.net/')

    def fetch_proxybros():
        try:
            with requests.Session() as sessions:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
                data = {
                    'action': 'nrproxyexport',
                    'type': '1',
                    'lang': 'ru',
                    'path': '/ru/free-proxy-list/http/',
                }
                sessions.post('https://proxybros.com/wp-admin/admin-ajax.php', headers=headers, data=data, timeout=10)
                response = sessions.get('https://proxybros.com/wp-json/proxy_list/download/', headers=headers, timeout=10)
                response_text = response.text
                lines = response_text.split('\n')
                ip = None
                proxybros_proxies = []
                for line in lines:
                    if line.startswith('IP Адрес:'):
                        ip = line.split(': ')[1].strip()
                    elif line.startswith('Порт:'):
                        port = line.split(': ')[1].strip()
                        if ip:
                            proxybros_proxies.append(f'{ip}:{port}')
                            ip = None
                proxies_collections['proxybros'] = proxybros_proxies
                print(f'[+] proxybros {len(proxies_collections.get("proxybros"))}')
        except:
            print(f'[-] proxybros')
            failed_request.append('https://proxybros.com/')

    def fetch_checkerproxy():
        try:
            main_url: str = 'https://checkerproxy.net/'
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
            r = requests.get(url=main_url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'lxml')
            block_ul = soup.find('div', class_='archive').find_all('li')[:2]
            proxies_url: list = []
            proxies_list: list = []
            for b in block_ul:
                href = 'https://checkerproxy.net/api' + b.find('a').get('href')
                proxies_url.append(href)

            for url in proxies_url:
                r = requests.get(url=url, headers=headers, timeout=10).json()
                for row in r:
                    ip = row.get('addr')
                    proxies_list.append(ip)
            proxies_collections['checkerproxy'] = proxies_list
            print(f'[+] checkerproxy {len(proxies_collections.get("checkerproxy"))}')
        except:
            print(f'[-] checkerproxy')
            failed_request.append('https://checkerproxy.net/')

    def fetch_my_proxy():
        try:
            main_url: str = 'https://www.my-proxy.com/free-proxy-list.html'
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
            r = requests.get(url=main_url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'lxml')
            block_ul = soup.find('div', class_='list')
            pattern = r'\d{1,3}(?:\.\d{1,3}){3}:\d+'
            string_ = block_ul.text
            proxies = re.findall(pattern, string_)
            block_ul2 = soup.find('div', class_='list').find('div', class_='to-lock')
            string_2 = block_ul2.text
            proxies2 = re.findall(pattern, string_2)
            proxies.extend(proxies2)
            proxies_collections['my-proxy'] = proxies
            print(f'[+] my-proxy {len(proxies_collections.get("my-proxy"))}')
        except:
            print(f'[-] my-proxy')
            failed_request.append('https://www.my-proxy.com/')

    def fetch_proxylistplus():
        try:
            main_url: str = 'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1'
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
            r = requests.get(url=main_url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'lxml')
            pagination = int(soup.find_all('option')[-1].text)
            proxies = []
            for page in range(1, pagination + 1):
                main_url: str = f'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{page}'
                r = requests.get(url=main_url, headers=headers, timeout=10)
                soup = BeautifulSoup(r.text, 'lxml')
                block_tr = soup.find_all('tr', class_='cells')
                for i in block_tr:
                    cells = i.find_all('td')
                    if len(cells) >= 3:
                        ip: str = cells[1].text.strip()
                        port: str = cells[2].text.strip()
                        if ip.isdigit() or port.isdigit():
                            proxy = f'{ip}:{port}'
                            proxies.append(proxy)
            proxies_collections['list.proxylistplus'] = proxies
            print(f'[+] list.proxylistplus {len(proxies_collections.get("list.proxylistplus"))}')
        except:
            print(f'[-] list.proxylistplus')
            failed_request.append('https://list.proxylistplus.com/')

    # Массив всех функций для многопоточной загрузки
    proxy_sources = [
        fetch_sslproxies,
        fetch_advanced_name,
        fetch_github,
        fetch_proxy_list,
        fetch_geonode,
        fetch_proxyscrape,
        fetch_spys,
        fetch_geoxy,
        fetch_fineproxy,
        fetch_spaceproxy,
        fetch_proxybros,
        fetch_checkerproxy,
        fetch_my_proxy,
        fetch_proxylistplus,
    ]


    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(func) for func in proxy_sources]
        for future in as_completed(futures):
            future.result()

    return proxies_collections


def update_proxy_file(proxies_collections, path_to_save):
    with open(path_to_save, 'w') as f:
        for source, proxies in proxies_collections.items():
            for proxy in proxies:
                f.write(f'{proxy} {source}\n')
    with open(path_to_save) as f:
        read = [i.strip() for i in f.readlines()]
        print(f'Total downloads: {len(read)}, Unique: {len(set(read))}\n')


def download(path_to_save):
    proxies_collections = fetch_proxies()
    if proxies_collections:
        update_proxy_file(proxies_collections, path_to_save)
