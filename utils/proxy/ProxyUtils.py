import requests
from bs4 import BeautifulSoup

from domain.exception.types.CustomException import CustomException

class ProxyUtils():
    
    def getProxyList():
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
    
    # FORBIDDEN
    def getProxyList2():
        try:
            url = "https://www.proxydocker.com/kr/proxylist/type/https"
            response = requests.get(url)

            if(response.status_code != 200):
                raise CustomException("request error.")

            dom = BeautifulSoup(response.text, "html.parser")
            proxyList = dom.select("#proxylist_table > tr")

            result = []
            for listEl in proxyList:
                address = listEl.select_one("td:nth-child(1) > a").text
                result.append(f"http://{address}")

            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)
        
    # RROXY CONNECTION ERROR
    def getProxyList3():
        try:
            # url = "https://proxyhub.me/ko/kr-https-proxy-list.htmls"
            # url = "https://proxyhub.me/"
            url = "https://proxyhub.me/en/all-https-proxy-list.html"
            response = requests.get(url)

            if(response.status_code != 200):
                raise CustomException("request error.")

            dom = BeautifulSoup(response.text, "html.parser")
            proxyList = dom.select("#main > div > div.list.table-responsive > table > tbody > tr")

            result = []
            for listEl in proxyList:
                ip = listEl.select_one("td:nth-child(1)").text
                port = listEl.select_one("td:nth-child(2)").text
                result.append(f"http://{ip}:{port}")

            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)


    # FORBIDDEN
    def getProxyList4():
        try:
            url = "https://premproxy.com/list/"
            response = requests.get(url)

            if(response.status_code != 200):
                raise CustomException("request error.")

            dom = BeautifulSoup(response.text, "html.parser")
            proxyList = dom.select("#proxylistt > tbody > tr")

            result = []
            for listEl in proxyList:
                ip = listEl.select_one("td:nth-child(1)").text
                port = listEl.select_one("td:nth-child(1) > .rf923").text
                result.append(f"http://{ip}:{port}")

            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)
        
    # PROXY CONNECTION ERRROR
    def getProxyList5():
        try:
            url = "https://www.freeproxylists.net/?c=&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0"
            response = requests.get(url)

            if(response.status_code != 200):
                raise CustomException("request error.")

            dom = BeautifulSoup(response.text, "html.parser")
            proxyList = dom.select("body > div:nth-child(3) > div:nth-child(2) > table > tbody > tr")

            result = []
            count = 0
            for listEl in proxyList:
                if(count == 0): continue
                ip = listEl.select_one("td:nth-child(1) > a").text
                port = listEl.select_one("td:nth-child(2)").text
                count += 1
                result.append(f"http://{ip}:{port}")

            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)
        
    