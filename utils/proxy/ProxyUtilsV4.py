import requests
from bs4 import BeautifulSoup

from exception.types.CustomException import CustomException

class ProxyUtilsV4():
    def __init__(self):
        self.proxies = self.initProxies()
        self.proxyServerIndex = 0

    # 프록시 서버 순서대로 사용
    def raiseProxyIndex(self):
        self.proxyServerIndex += 1

    def initProxies(self):
        try:
            result = []
            url = "https://free-proxy-list.net"
            response = requests.get(url)

            if(response.status_code != 200):
                raise CustomException("request error for free proxy list.")

            dom = BeautifulSoup(response.text, "html.parser")
            proxyList = dom.select("#list > div > div.table-responsive > div > table > tbody > tr")

            for listEl in proxyList:
                if(listEl.select_one(".hx").text == "yes"):
                    ip = listEl.select_one("td:nth-child(1)").text
                    port = listEl.select_one("td:nth-child(2)").text
                    result.append(f"http://{ip}:{port}")

            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)
    
    def getProxyInOrder(self):
        proxyAddress = self.proxies[self.proxyServerIndex]
        self.raiseProxyIndex()
        return proxyAddress
    
    def isLeftProxy(self):
        if self.proxyServerIndex >= len(self.proxies):
            return False
        return True

    