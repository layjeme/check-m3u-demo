import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import httpx
import random
from time import sleep
from m3u_parser import M3uParser
import urllib3

def sleep_random():
    """随机等待1-5秒防止IP被封"""
    sleep_s = random.randint(1, 5)
    sleep(sleep_s)


def check_url_ok(url):
    """检测连接是否可用"""
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        # 'Connection': 'keep-alive',
        'Connection': 'close',
    }

    print("正在检查URL %s" % url)
    # s.proxies = {"https": "https://114.98.114.180:3256", "http": "http://114.98.114.180:3256"}

    try:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # 忽略警告
        result = requests.get(url, headers=headers, timeout=(5, 5))

        if result.status_code == 200:

            print("访问正常 %s" % url)
            return True
        else:
            print("访问失败 %s" % url)
            return False
    except Exception as e:
        print(e)
        return False



def check_url_status(url):
    """检测连接是否可用"""
    useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
    print("正在检查URL %s" % url)
    httpx.DEFAULT_RETRIES = 5  # 增加重试连接次数
    # requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
    # s = requests.session()
    # s.keep_alive = False  # 关闭多余连接
    # urllib3.disable_warnings()  # 忽略警告
    # s.proxies = {"https": "https://114.98.114.180:3256", "http": "http://114.98.114.180:3256"}

    result = httpx.get(url, headers={"User-Agent": useragent}, timeout=5, verify=False)

    if result.status_code == 200:

        print("访问正常 %s" % url)
        return True
    else:
        print("访问失败 %s" % url)
        return False