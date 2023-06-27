import requests
from bs4 import BeautifulSoup
import json
import time
from requests.exceptions import ProxyError, SSLError, ConnectTimeout, ReadTimeout, ChunkedEncodingError, ConnectionError
from fake_useragent import UserAgent
import asyncio

from domain.naver_rank.dto.NaverRankDto import NaverRankDto
from domain.exception.types.CustomException import CustomException
from utils.proxy.ProxyUtilsV3 import ProxyUtils
from utils.time.TimeUtils import TimeUtils

DEFAULT_PAGINGSIZE = 80
MAX_SEARCH_PAGE_SIZE = 10

NAVER_SHOPPINT_RANK_URL = "https://search.shopping.naver.com/search/all"
REQUEST_TIMEOUT_SIZE = 10

class NaverRankService():
    startTime = 0

    def __init__(self, keyword, mallName):
        self.keyword = keyword
        self.mallName = mallName

    async def getCurrentPageResponse(self, pageIndex, proxyUtils):
        params = {
            'frm': 'NVSHTTL',
            'pagingIndex': pageIndex,
            'pagingSize': DEFAULT_PAGINGSIZE,
            'query': self.keyword,
            'sort': 'rel',
            'productSet': 'total',
        }

        response = None
        productList = []
        # 프록시 서버를 이용해 api request가 성공할 때까지
        while(True):
            print(TimeUtils.getDifferenceFromCurrentTime(NaverRankService.startTime))
            # if(REQUEST_TIMEOUT_SIZE < TimeUtils.getDifferenceFromCurrentTime(NaverRankService.startTime)): 
            #     raise TimeoutError

            proxyAddress = proxyUtils.getProxyInOrder()
            proxy = {'http': proxyAddress, 'https': proxyAddress}
            headers = {"user-agent": UserAgent().random}

            try:
                response = requests.get(url=NAVER_SHOPPINT_RANK_URL, proxies=proxy, headers=headers, verify=False, timeout=5, params=params)
                # response = requests.get(url=NAVER_SHOPPINT_RANK_URL, headers=headers, verify=False, timeout=5, params=params)
            except (ProxyError, SSLError, ConnectTimeout, ReadTimeout, ConnectionError, ChunkedEncodingError):
                print("proxy connection error.")
                continue
        
            if(response.status_code != 200):
                proxyUtils.removeForbiddenProxy(proxyAddress)
                print("api request error.")
                continue
        
            try:
                dom = BeautifulSoup(response.text, "html.parser")
                resultObj = dom.select_one("#__NEXT_DATA__").text
                productJsonObj = json.loads(resultObj)
                productList = productJsonObj['props']['pageProps']['initialState']['products']['list']
            except (KeyError, AttributeError, UnboundLocalError, TypeError):
                # 응답이 올바르지만, request api attribute가 올바르지 않는다면 다음 프록시 요청
                print("response attribute error.")
                continue
            
            break
        
        # 정상적인 응답을 받은 proxy 서버의 우선순위 증가
        proxyUtils.raiseProxyPriority(proxyAddress)
        return productList

    async def requestSearchPage(self, pageIndex, proxyUtils):
        print(pageIndex)
        # get response for naver ranking page
        # getCurrentPageResponse 코루틴 등록
        searchResponse = await asyncio.create_task(self.getCurrentPageResponse(pageIndex, proxyUtils))

        try:
            # 여러 상품이 노출될 수 있으므로 list로 return
            result = []
            rank = 0
            for productObj in searchResponse: 
                dto = NaverRankDto(self.mallName)
                item = productObj['item']
                rank += 1

                if (item['mallName'] == self.mallName):
                    dto.setRank(rank)
                    dto.setExcludedAdRank(item['rank'])
                    dto.setProductTitle(item['productTitle'])
                    dto.setPrice(item['price'])
                    dto.setPage(pageIndex)
                    dto.setMallProductId(item['mallProductId'])
                    if('adId' in item):
                        dto.setIsAdvertising(True)

                if (item['lowMallList'] is not None):
                    comparitionList = item['lowMallList']
                    comparitionRank = 0
                    for comparitionItem in comparitionList:
                        comparitionRank += 1
                        if (comparitionItem['name'] == self.mallName):
                            dto.setRank(rank)
                            dto.setExcludedAdRank(item['rank'])
                            dto.setIsPriceComparision(True)
                            dto.setComparisionRank(comparitionRank)
                            dto.setProductTitle(item['productTitle'])
                            dto.setPrice(comparitionItem['price'])
                            dto.setPage(pageIndex)
                            dto.setMallProductId(comparitionItem['mallPid'])
                            break
                       
                if dto.rank != 0:
                    result.append(dto.__dict__)
            
            await asyncio.sleep(2)
            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)
    
    async def setTimeout(self):
        print("hi")
        await asyncio.sleep(5)
        print("timeout!")
        raise TimeoutError
    
    async def searchTest(self):
        await asyncio.gather(*[self.setTimeout(), self.searchRank2()])

    async def searchRank2(self):
        await self.searchRank()
        
    async def searchRank(self):
        NaverRankService.startTime = time.perf_counter()
        proxyUtils = ProxyUtils(MAX_SEARCH_PAGE_SIZE)
        
        # asyncio.gather()로 비동기로 여러개의 작업을 등록
        # return_exceptions=True면 예외가 핸들링되지 않고 예외 클래스 리턴됨. False면 첫 번째 발생한 예외가 대기중인 작업에 전파되고 예외핸들링 가능.
        results = []
        responses = []
        try:
            responses = await asyncio.gather(*[self.requestSearchPage(i+1, proxyUtils) for i in range(MAX_SEARCH_PAGE_SIZE)], return_exceptions=False)

            for response in responses:
                results.extend(response)
                
        except TimeoutError:
            raise TimeoutError("request time out.")
        
        return results
    