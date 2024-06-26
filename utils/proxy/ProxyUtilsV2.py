import requests
from bs4 import BeautifulSoup

from exception.types.CustomException import CustomException

class ProxyUtilsV2():
    def __init__(self):
        self.proxies = ProxyUtilsV2.initProxies()
        self.proxyServerIndex = 0

    def setProxyServerIndex(self, proxyServerIndex):
        self.proxyServerIndex = proxyServerIndex

    def initProxies():
        try:
            url = "https://free-proxy-list.net"
            response = requests.get(url)

            if(response.status_code != 200):
                raise CustomException("request error.")

            dom = BeautifulSoup(response.text, "html.parser")
            proxyList = dom.select("#list > div > div.table-responsive > div > table > tbody > tr")

            result = []
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
        
    # proxy server address 순서대로 조회
    def getProxyInOrder(self):
        if(len(self.proxies) <= self.proxyServerIndex):
            raise CustomException("can't connect all proxy servers.")
        
        proxyAddress = self.proxies[self.proxyServerIndex]
        self.setProxyServerIndex(self.proxyServerIndex + 1)

        return proxyAddress

    