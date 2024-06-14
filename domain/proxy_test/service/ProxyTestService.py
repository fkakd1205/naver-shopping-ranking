from bs4 import BeautifulSoup
import json
from fake_useragent import UserAgent
import asyncio
import aiohttp
import requests
import time

from aiohttp.client_exceptions import ClientProxyConnectionError, ClientOSError, ClientHttpProxyError

from utils.proxy.ProxyUtilsV4 import ProxyUtilsV4

NAVER_SHOPPINT_RANK_URL = "https://search.shopping.naver.com/search/all"
DEFAULT_PAGINGSIZE = 80

TOTAL_REQUEST_TIMEOUT_SIZE = 60
# UNIT_REQUEST_TIMEOUT_SIZE = 30
UNIT_REQUEST_TIMEOUT_SIZE = 10

class ProxyTestService():
    def __init__(self, keyword, mallName, pageSize):
        self.keyword = keyword
        self.mallName = mallName
        self.pageSize = pageSize
        self.proxyUtils = ProxyUtilsV4()

    def search_rank(self):
        while(True):
            proxyAddress = self.proxyUtils.getProxyInOrder() # 사용할 프록시 서버를 순서대로 조회
            proxy = {'http': proxyAddress, 'https': proxyAddress}
            headers = {"user-agent": UserAgent().random}

            try:
                html = requests.get(
                 url=NAVER_SHOPPINT_RANK_URL,
                 proxies=proxy,
                 headers=headers,
                 verify=False,
                 timeout=5)
                print(html.text)
            except (ConnectionRefusedError, ClientProxyConnectionError, ClientOSError, ClientHttpProxyError):
                print("proxy connection error")
                continue
            except asyncio.TimeoutError:
                print("proxy connection time out")
                continue
            except aiohttp.ServerDisconnectedError:
                print("server does not accept request")
                continue

            try:
                dom = BeautifulSoup(html, "html.parser")
                resultObj = dom.select_one("#__NEXT_DATA__").text
                productJsonObj = json.loads(resultObj)
                productList = productJsonObj['props']['pageProps']['initialState']['products']['list']
            except (KeyError, AttributeError, UnboundLocalError, TypeError):
                # 응답은 넘어오지만, response attribute가 올바르지 않다면
                print("response attribute error")
                continue

        return productList
