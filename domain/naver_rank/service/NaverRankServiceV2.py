import requests
from bs4 import BeautifulSoup
import json
import time
from concurrent import futures
from requests.exceptions import ProxyError, SSLError, ConnectTimeout, ReadTimeout, ChunkedEncodingError, ConnectionError
from fake_useragent import UserAgent

from domain.naver_rank.dto.NaverRankDto import NaverRankDto
from domain.exception.types.CustomException import CustomException
from utils.proxy.ProxyUtilsV3 import ProxyUtils
from utils.time.TimeUtils import TimeUtils

DEFAULT_PAGINGSIZE = 80
MAX_SEARCH_PAGE_SIZE = 10

NAVER_SHOPPINT_RANK = "https://search.shopping.naver.com/search/all"
REQUEST_TIMEOUT_SIZE = 15

class NaverRankService():
    startTime = 0

    def __init__(self, keyword, mallName):
        self.keyword = keyword
        self.mallName = mallName

    def getCurrentPageResponse(self, pageIndex, proxyUtils):        
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
        # 프록시 서버를 이용해 api request가 성공할 때 까지
        while(True):
            if(REQUEST_TIMEOUT_SIZE < TimeUtils.getDifferenceFromCurrentTime(NaverRankService.startTime)): 
                raise TimeoutError

            proxyAddress = proxyUtils.getProxyInOrder()
            proxy = {'http': proxyAddress, 'https': proxyAddress}
            headers = {"user-agent": UserAgent().random}

            try:
                response = requests.get(url=NAVER_SHOPPINT_RANK, proxies=proxy, headers=headers, verify=False, timeout=5, params=params)
            except (ProxyError, SSLError, ConnectTimeout, ReadTimeout, ConnectionError):
                print("proxy connection error.")
                continue
            except ChunkedEncodingError:
                print("chunked encoding error.")
                continue
        
            # api 요청 거절 시 예외 처리
            if(response.status_code != 200):
                proxyUtils.removeForbiddenProxy(proxyAddress)
                print("api request error.")
                continue
                # raise CustomException("api request error.")
        
            try:
                dom = BeautifulSoup(response.text, "html.parser")

                resultObj = dom.select_one("#__NEXT_DATA__").text
                productJsonObj = json.loads(resultObj)
            
                productList = productJsonObj['props']['pageProps']['initialState']['products']['list']
            except (KeyError, AttributeError, UnboundLocalError, TypeError):
                # 응답이 올바르지만, request api attribute가 올바르지 않는다면 다음 프록시 요청
                print("api attribute error.")
                continue

            print(proxyAddress + " success!!!")
            # api response가 올바르다면 while문 탈출
            break
        
        proxyUtils.raiseProxyPriority(proxyAddress)
        return productList

    def requestSearchPage(self, pageIndex, proxyUtils):
        # naver ranking page response
        searchResponse = self.getCurrentPageResponse(pageIndex, proxyUtils)

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
            
            time.sleep(2)
            return result
        except KeyError as e:
            raise CustomException(f"not found value for {e}")
        except AttributeError as e:
            raise CustomException(e)

    def searchRank(self):
        NaverRankService.startTime = time.perf_counter()
        proxyUtils = ProxyUtils(MAX_SEARCH_PAGE_SIZE)

        # 멀티쓰레드 생성
        # MAX_SEARCH_PAGE_SIZE 만큼 반복
        rankDtos = []
        results = []
        with futures.ThreadPoolExecutor() as executor:
            rankDtos = [executor.submit(self.requestSearchPage, i+1, proxyUtils) for i in range(MAX_SEARCH_PAGE_SIZE)]

            try:
                for f in futures.as_completed(rankDtos):
                    results.extend(f.result())
            except TimeoutError:
                # wait=True로 설정한다면 실행중인 모든 작업이 완료될 때까지 호출이 반환되지 않는다
                # cancel_futures가 True이면 보류 중인 모든 Future가 취소된다. 완료되거나 실행 중인 Future는 취소되지 않음
                executor.shutdown(wait=False, cancel_futures=True)
                raise TimeoutError("request timed out.")

        return results
