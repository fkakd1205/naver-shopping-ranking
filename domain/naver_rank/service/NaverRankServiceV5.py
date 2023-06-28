from bs4 import BeautifulSoup
import json
import time
from fake_useragent import UserAgent
import asyncio
import aiohttp

from aiohttp.client_exceptions import ClientProxyConnectionError, ClientOSError, ClientHttpProxyError

from domain.naver_rank.dto.NaverRankDto import NaverRankDto
from exception.types.CustomException import CustomException
# from utils.proxy.ProxyUtilsV3 import ProxyUtils
from utils.time.TimeUtils import TimeUtils

DEFAULT_PAGINGSIZE = 80
MAX_SEARCH_PAGE_SIZE = 3

NAVER_SHOPPINT_RANK_URL = "https://search.shopping.naver.com/search/all"
TOTAL_REQUEST_TIMEOUT_SIZE = 60
UNIT_REQUEST_TIMEOUT_SIZE = 30

class NaverRankService():
    startTime = 0

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

        # 프록시 서버를 이용해 api request가 성공할 때까지
        while(True):
            print(TimeUtils.getDifferenceFromCurrentTime(NaverRankService.startTime))
            
            proxyAddress = "http://kr.smartproxy.com:10000"
            headers = {"user-agent": UserAgent().random}

            try:
                async with aiohttp.ClientSession() as session:
                    res = await session.get(url=NAVER_SHOPPINT_RANK_URL, proxy = proxyAddress, timeout=UNIT_REQUEST_TIMEOUT_SIZE, headers=headers, params=params)
                    response = await res.text()
            except (ConnectionRefusedError, ClientProxyConnectionError, ClientOSError, ClientHttpProxyError):
                print("proxy connection error.")
                continue
            except asyncio.TimeoutError:
                print("proxy connection time out")
                continue
            except Exception as e:
                # ServerDisconnectedError 캐치해야함
                e.with_traceback()
                print("undefined error")
        
            try:
                dom = BeautifulSoup(response, "html.parser")
                resultObj = dom.select_one("#__NEXT_DATA__").text
                productJsonObj = json.loads(resultObj)
                productList = productJsonObj['props']['pageProps']['initialState']['products']['list']
            except (KeyError, AttributeError, UnboundLocalError, TypeError):
                # 응답이 올바르지만, request api attribute가 올바르지 않는다면 다음 프록시 요청
                print("response attribute error.")
                continue
            
            return productList

    async def requestPageAndGetRankDtos(self, pageIndex):
        print(pageIndex)
        # get response for naver ranking page
        searchResponse = await asyncio.create_task(self.getCurrentPageResponse(pageIndex))

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
            
            # time.sleep(2)
            # await asyncio.sleep(2)
            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)
        
    async def setTimeout(self):
        print("setTimeout() start")
        await asyncio.sleep(TOTAL_REQUEST_TIMEOUT_SIZE)
        print("change isTimeout")
        self.isTimeout = True
        raise TimeoutError("setTimout error")
    
    # async def setTimeout2(self):
    #     print("setTimeout2() start")
    #     requests = [self.setTimeout3() for _ in range(3)]
    #     await asyncio.gather(*requests)

    # async def setTimeout3(self):
    #     print("setTimeout3 start")
    #     await asyncio.sleep(5)
    #     print("setTimeout3 finish")


    # async def searchTest(self):
    #     task1 = asyncio.create_task(self.setTimeout())
    #     task2 = asyncio.create_task(self.searchRank())
        
    #     try:
    #         await task1
    #     except TimeoutError as e:
    #         cancelled = task2.cancel()
    #         raise TimeoutError(e)
        
    #     await task2

    #     return task2.result()

    async def searchRank(self):
        task = asyncio.create_task(self.searchTotalPage())

        try:
            # timeout 설정한 시간만큼 기다린다. 초과되면 예외발생 후 바로 리턴
            await asyncio.wait_for(task, timeout=TOTAL_REQUEST_TIMEOUT_SIZE)
        except (asyncio.TimeoutError) as e:
            task.cancel()
            raise TimeoutError(e)
        
        return task.result()

    # async def searchRank(self):
    #     print("searchRank")
    #     NaverRankService.startTime = time.perf_counter()
    #     proxyUtils = ProxyUtils(MAX_SEARCH_PAGE_SIZE)
        
    #     # 멀티쓰레드 생성
    #     # MAX_SEARCH_PAGE_SIZE 만큼 반복
    #     rankDtos = []
    #     results = []
    #     with futures.ThreadPoolExecutor() as executor:
    #         rankDtos = [executor.submit(self.requestSearchPage, i+1, proxyUtils) for i in range(MAX_SEARCH_PAGE_SIZE)]

    #         try:
    #             for f in futures.as_completed(rankDtos):
    #                 results.extend(f.result())
    #         except TimeoutError:
    #             # wait=True로 설정한다면 실행중인 모든 작업이 완료될 때까지 호출이 반환되지 않는다
    #             # cancel_futures가 True이면 보류 중인 모든 Future가 취소된다. 완료되거나 실행 중인 Future는 취소되지 않음.
    #             # cancel_future가 False이면 보류 중인 Future가 취소되지 않는다. 대기상태는 계속해서 실행됨
    #             executor.shutdown(wait=False, cancel_futures=True)
    #             raise TimeoutError("request timed out.")
            
    #     return results

    # async def searchRank(self):
    #     print("searchRank() start")
    #     NaverRankService.startTime = time.perf_counter()
    #     proxyUtils = ProxyUtils(MAX_SEARCH_PAGE_SIZE)
        
    #     # 멀티쓰레드 생성
    #     # MAX_SEARCH_PAGE_SIZE 만큼 반복
    #     results = []
    #     rankDtos = []
    #     loop = asyncio.get_running_loop()
    #     with futures.ThreadPoolExecutor() as executor:
    #         rankDtoFutures = [loop.run_in_executor(executor, self.requestSearchPage, i+1, proxyUtils) for i in range(MAX_SEARCH_PAGE_SIZE)]
    #         # rankDtoFutures = [self.requestSearchPage(i+1, proxyUtils) for i in range(MAX_SEARCH_PAGE_SIZE)]

    #         try:
    #             rankDtos = await asyncio.gather(*rankDtoFutures, return_exceptions=False)
    #         except TimeoutError as e:
    #             executor.shutdown(wait=False, cancel_futures=True)
    #             print("search rank exception!!")
    #             raise TimeoutError(e)

    #         for dto in rankDtos:
    #             results.extend(dto)

    #     return results

    async def searchTotalPage(self):
        print("searchRank() start")
        NaverRankService.startTime = time.perf_counter()
        # proxyUtils = ProxyUtils(MAX_SEARCH_PAGE_SIZE)
        
        # 멀티쓰레드 생성
        # MAX_SEARCH_PAGE_SIZE 만큼 반복
        results = []
        rankDtos = [self.requestPageAndGetRankDtos(i+1) for i in range(MAX_SEARCH_PAGE_SIZE)]
        rankResults = await asyncio.gather(*rankDtos)

        for result in rankResults:
            results.extend(result)

        return results
