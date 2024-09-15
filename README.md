# proxsiesCheker
The program downloads a list of free HTTP/HTTPS from 14 sites. It is also possible to asynchronously check the functionality of downloaded proxies for the target site. For example, to work on the site examlpe.com you need proxies, you can download them and then check how many proxies will currently work with this site.

## Installation
```bash
git clone https://github.com/prt-SSS/proxsiesCheker.git
cd proxsiesCheker
windows: python -m venv venv | linux python3 -m venv venv
windows: .venv\Scripts\activate | linux: source venv/bin/activate
windows: pip install -r requirements.txt | linux: pip3 install -r requirements.txt
windows: python run.py | linux python3 run.py
