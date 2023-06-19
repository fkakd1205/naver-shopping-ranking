from flask_restx import Namespace, Resource
from requests.exceptions import ProxyError, SSLError, ConnectTimeout, ReadTimeout, ChunkedEncodingError, ConnectionError
import requests

from utils.proxy.ProxyUtilsV2 import ProxyUtilsV2

TestApi = Namespace('TestApi')

@TestApi.route('', methods=['GET'])
class Test(Resource):
    def get(self):
        url = ("http://dev.api.piaar.co.kr/api/v1/test")

        proxyUtils = ProxyUtilsV2()
        headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

        while(True):
            proxyAddress = proxyUtils.getProxyInOrder()
            proxy = {'http': proxyAddress, 'https': proxyAddress}
            
            try:
                response = requests.get(url, proxies=proxy, headers=headers, verify=False, timeout=5)
            except (ProxyError, SSLError, ConnectTimeout, ReadTimeout, ConnectionError) as e:
                # proxy connection error 발생 시 다음 프록시 요청
                print("proxy connection error.")
                print(e)
                continue
            except ChunkedEncodingError:
                print("chunked encoding error.")
                continue
            

            if(response.status_code == 200): break
    
        print(response.text)