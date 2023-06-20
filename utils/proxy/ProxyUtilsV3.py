import requests
from bs4 import BeautifulSoup

from domain.exception.types.CustomException import CustomException

class ProxyUtils():
    """
    proxies : dict
    searchableCount : int

    argument -- requestCount

    __init__(self, requestCount) : reuqestCount를 전달받아 searchableCount(검색가능 카운트) 설정
    refresh(self) : proxies를 초기화. {proxy: 기존 proxy server, isConnected: False}로 업데이트
    subSearchableCount(self) : searchableCount를 1 감소
    Return: ProxyUtils
    """
    def __init__(self, requestCount):
        proxyDict = ProxyUtils.initProxies()
        self.proxies = proxyDict
        self.searchableCount = (requestCount * 3) if (requestCount * 3) > len(proxyDict) else len(proxyDict)

    def refresh(self):
        """
        proxies의 isConnected를 모두 초기화
        """
        result = []
        for p in self.proxies:
            result.append({'proxy': p.get('proxy'), 'isConnected': False})
        
        self.proxies = result

    def subSearchableCount(self):
        self.searchableCount -= 1

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
                    result.append({'proxy': f"http://{ip}:{port}", 'isConnected': False})

            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)

    # proxy server address 순서대로 조회
    def getProxyInOrder(self):
        proxyAddress = None

        # 조회된 proxy server가 없는 경우
        if(len(self.proxies) <= 0):
            raise CustomException("https proxy server not available.")

        # searchableCount를 초과한 경우
        if(self.searchableCount <= 0):
            raise CustomException("proxy searchable count exceeded.")
        
        for proxy in self.proxies:
            if(proxy.get('isConnected') == False):
                proxy['isConnected'] = True
                proxyAddress = proxy.get('proxy')
                self.subSearchableCount()
                break
        
        # proxies를 모두 연결한 경우, refresh시켜 isConnected초기화
        if proxyAddress is None:
            self.refresh()
            for proxy in self.proxies:
                if(proxy.get('isConnected') == False):
                    proxy['isConnected'] = True
                    proxyAddress = proxy.get('proxy')
                    self.subSearchableCount()
                    break

        return proxyAddress
    