from bs4 import BeautifulSoup
import json
from fake_useragent import UserAgent
import asyncio
import aiohttp

from aiohttp.client_exceptions import ClientProxyConnectionError, ClientOSError, ClientHttpProxyError

from domain.naver_rank.dto.NaverRankDto import NaverRankDto
from exception.types.CustomException import CustomException

DEFAULT_PAGINGSIZE = 80
MAX_SEARCH_PAGE_SIZE = 2

PROXY_REQUEST_URL = "http://kr.smartproxy.com:10000"
NAVER_SHOPPINT_RANK_URL = "https://search.shopping.naver.com/search/all"
TOTAL_REQUEST_TIMEOUT_SIZE = 60
UNIT_REQUEST_TIMEOUT_SIZE = 30

class NaverRankService():

    def __init__(self, keyword, mallName):
        self.keyword = keyword
        self.mallName = mallName

    async def getCurrentPageResponse(self, pageIndex):
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

        # 프록시 서버를 이용해 request 응답이 성공할 때까지 요청을 중단하지 않는다
        while(True):
            headers = {"user-agent": UserAgent().random}

            try:
                async with aiohttp.ClientSession() as session:
                    res = await session.get(
                        url=NAVER_SHOPPINT_RANK_URL,
                        proxy = PROXY_REQUEST_URL,
                        timeout=UNIT_REQUEST_TIMEOUT_SIZE,
                        headers=headers,
                        params=params
                        )
                    response = await res.text()
            except (ConnectionRefusedError, ClientProxyConnectionError, ClientOSError, ClientHttpProxyError):
                print("proxy connection error.")
                continue
            except asyncio.TimeoutError:
                print("proxy connection time out")
                continue
            except aiohttp.ServerDisconnectedError:
                print("server does not accept request")
                continue
        
            try:
                dom = BeautifulSoup(response, "html.parser")
                resultObj = dom.select_one("#__NEXT_DATA__").text
                productJsonObj = json.loads(resultObj)
                productList = productJsonObj['props']['pageProps']['initialState']['products']['list']
            except (KeyError, AttributeError, UnboundLocalError, TypeError):
                # 응답은 넘어오지만, response attribute가 올바르지 않는다면 다음 프록시 요청
                print("response attribute error.")
                continue
            
            return productList

    async def requestPageAndGetRankDtos(self, pageIndex):
        # get response by naver ranking page
        searchResponse = await asyncio.create_task(self.getCurrentPageResponse(pageIndex))

        try:
            # 한 페이지에 여러 상품이 노출될 수 있으므로 list 반환
            result = []
            rank = DEFAULT_PAGINGSIZE * (pageIndex-1)
            for responseObj in searchResponse: 
                dtos = []
                item = responseObj['item']
                rank += 1

                if (item['mallName'] == self.mallName):
                    dto = NaverRankDto(self.mallName)
                    dto.setRank(rank)
                    dto.setExcludedAdRank(item['rank'])
                    dto.setProductTitle(item['productTitle'])
                    dto.setPrice(item['price'])
                    dto.setPage(pageIndex)
                    dto.setMallProductId(item['mallProductId'])
                    if('adId' in item):
                        dto.setIsAdvertising(True)

                    dtos.append(dto.__dict__)

                # 가격비교 쇼핑몰 검색
                # lowMallList = null or []
                if (item['lowMallList'] is not None):
                    comparitionRank = 0
                    for comparitionItem in item['lowMallList']:
                        comparitionRank += 1
                        if (comparitionItem['name'] == self.mallName):
                            dto = NaverRankDto(self.mallName)
                            dto.setRank(rank)
                            dto.setExcludedAdRank(item['rank'])
                            dto.setIsPriceComparision(True)
                            dto.setComparisionRank(comparitionRank)
                            dto.setProductTitle(item['productTitle'])
                            dto.setPrice(comparitionItem['price'])
                            dto.setPage(pageIndex)
                            dto.setMallProductId(comparitionItem['mallPid'])
                            
                            dtos.append(dto.__dict__)

                result.extend(dtos)
            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)

    # check timeout and search request page
    # 전체 요청시간이 TOTAL_REQUEST_TIMEOUT_SIZE를 초과한다면 기다리지 않고 예외처리
    async def searchRank(self):
        
        task = asyncio.create_task(self.searchTotalPage())

        try:
            await asyncio.wait_for(task, timeout=TOTAL_REQUEST_TIMEOUT_SIZE)
        except (asyncio.TimeoutError) as e:
            task.cancel()
            raise TimeoutError(e)
        
        return task.result()

    async def searchTotalPage(self):
        results = []

        # MAX_SEARCH_PAGE_SIZE 만큼 비동기 요청
        rankDtos = [self.requestPageAndGetRankDtos(i+1) for i in range(MAX_SEARCH_PAGE_SIZE)]
        rankResults = await asyncio.gather(*rankDtos)

        for result in rankResults:
            results.extend(result)

        return results
