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
            type(dom)

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
