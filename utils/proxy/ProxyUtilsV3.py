import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout, ConnectionError

from exception.types.CustomException import CustomException

MULTIPLE_COUNT = 5

class ProxyUtils():
    """
    proxies : dict
    searchableCount : int

    argument -- requestCount

    __init__(self, requestCount) : reuqestCount를 전달받아 searchableCount(검색가능 카운트) 설정
    refreshProxy(self) : proxies를 초기화. {proxy: 기존 proxy server, isConnected: False}로 업데이트
    removeForbiddenProxy(self, proxy) : 금지된 proxy를 전달받아 proxies에서 제거
    raiseProxyPriority(self, proxy) : 요청이 성공된 proxy를 전달받아 우선순위 증가
    subSearchableCount(self) : searchableCount를 1 감소
    Return: ProxyUtils
    """
    def __init__(self, requestCount):
        proxyDict = ProxyUtils.initProxies()
        reqCount = (requestCount * MULTIPLE_COUNT) if (requestCount * MULTIPLE_COUNT) > len(proxyDict) else len(proxyDict)

        self.proxies = proxyDict
        self.searchableCount = reqCount

    def refreshProxy(self):
        """
        proxies의 isConnected를 모두 초기화
        우선순위가 큰 순으로 재정렬
        """
        result = []
        proxies = self.proxies
        proxies.sort(key=lambda p: p.get('priority'), reverse=True)
        for p in proxies:
            result.append({'proxy': p.get('proxy'), 'isConnected': False, 'priority': p.get('priority')})
        
        self.setProxies(result)

    def removeForbiddenProxy(self, proxy):
        """
        forbidden proxy 제거
        """
        result =[]
        for p in self.proxies:
            if(p.get('proxy') != proxy):
                result.append(p)

        self.setProxies(result)
        
    def raiseProxyPriority(self, proxy):
        """
        요청이 성공한 proxy의 우선순위를 증가
        """
        result = []
        for p in self.proxies:
            if(p.get('proxy') == proxy):
                result.append({'proxy': p.get('proxy'), 'isConnected': False, 'priority': p.get('priority') + 1})
                continue
            result.append(p)

        self.setProxies(result)
        
    def subSearchableCount(self):
        self.searchableCount -= 1

    def setProxies(self, proxies):
        self.proxies = proxies

    def initProxies():
        try:
            url = "https://free-proxy-list.net"
            response = requests.get(url, verify=False, timeout=3)

            if(response.status_code != 200):
                raise CustomException("proxy list request error.")

            dom = BeautifulSoup(response.text, "html.parser")
            proxyList = dom.select("#list > div > div.table-responsive > div > table > tbody > tr")

            result = []
            for listEl in proxyList:
                if(listEl.select_one(".hx").text == "yes"):
                    ip = listEl.select_one("td:nth-child(1)").text
                    port = listEl.select_one("td:nth-child(2)").text
                    result.append({'proxy': f"http://{ip}:{port}", 'isConnected': False, 'priority': 0})

            return result
        except (ConnectionError, ConnectTimeout):
            raise CustomException("proxy server search error.")
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
            self.refreshProxy()
            return self.getProxyInOrder()

        return proxyAddress
    