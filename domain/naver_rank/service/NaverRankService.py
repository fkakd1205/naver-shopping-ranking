import requests
from bs4 import BeautifulSoup
import json
import time
from concurrent import futures
from threading import Lock
from requests.exceptions import ProxyError, SSLError, ConnectTimeout, ReadTimeout, ChunkedEncodingError, ConnectionError
from fake_useragent import UserAgent

from domain.naver_rank.dto.NaverRankDto import NaverRankDto
from domain.exception.types.CustomException import CustomException
from utils.proxy.ProxyUtils import ProxyUtils

DEFAULT_PAGINGSIZE = 80
MAX_SEARCH_PAGE_SIZE = 4

proxyServerIndex = 0
lock = Lock()

class NaverRankService():
    proxies = ProxyUtils.getProxyList()
    # proxies = ProxyUtils.getProxyList2()
    # proxies = ProxyUtils.getProxyList3()
    # proxies = ProxyUtils.getProxyList4()
    # proxies = ProxyUtils.getProxyList5()

    # proxy server address 순서대로 조회
    def getProxyServerAddress(self):
        global proxyServerIndex
        proxyList = self.proxies

        # thread lock 설정. proxyServerIndex를 순서대로 가져오기 위해
        lock.acquire()
        print(proxyServerIndex)
        if(len(proxyList) <= proxyServerIndex):
            lock.release()
            raise CustomException("can't connect all proxy servers.")
        
        proxyAddress = proxyList[proxyServerIndex]
        proxyServerIndex += 1
        lock.release()
        # thread lock 해제.

        return proxyAddress

    def requestSearchPage(keyword, pageIndex):
        service = NaverRankService()
        
        url = ("https://search.shopping.naver.com/search/all"
        f"?frm=NVSCPRO"
        f"&origQuery={keyword}"
        f"&pagingIndex={pageIndex}"
        f"&pagingSize={DEFAULT_PAGINGSIZE}"
        f"&productSet=total"
        f"&query={keyword}"
        f"&sort=rel"
        f"&timestamp="
        f"&viewType=list"
        )
        
        response = None
        productList = []
        # 프록시 서버를 이용해 api request가 성공할 때 까지
        while(True):
            proxyAddress = service.getProxyServerAddress()
            proxy = {'http': proxyAddress, 'https': proxyAddress}

            # fake user agent setting
            headers = {"user-agent": UserAgent().random}

            try:
                response = requests.get(url, proxies=proxy, headers=headers, verify=False, timeout=5)
            except (ProxyError, SSLError, ConnectTimeout, ReadTimeout, ConnectionError):
                # proxy connection error 발생 시 다음 프록시 요청
                print("proxy connection error.")
                continue
            except ChunkedEncodingError:
                print("chunked encoding error.")
                continue
        
            # # api 요청 거절 시 예외 처리
            if(response.status_code != 200):
                raise CustomException("api request error.")
        
            try:
                dom = BeautifulSoup(response.text, "html.parser")

                resultObj = dom.select_one("#__NEXT_DATA__").text
                productJsonObj = json.loads(resultObj)
            
                productList = productJsonObj['props']['pageProps']['initialState']['products']['list']
            except (KeyError, AttributeError, UnboundLocalError, TypeError):
                # 응답이 올바르지만, request api attribute가 올바르지 않는다면 다음 프록시 요청
                print("api attribute error.")
                continue

            # api response가 올바르다면 while문 탈출
            if(response.status_code == 200): break

        return productList

    def searchCurrentPageRank(productList, mallName, pageIndex):
        try:
            # 여러 상품이 노출될 수 있으므로 list로 return
            result = []
            rank = 0
            for productObj in productList: 
                dto = NaverRankDto(mallName)
                item = productObj['item']
                rank += 1

                if (item['mallName'] == mallName):
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
                        if (comparitionItem['name'] == mallName):
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

    
    def searchRank(keyword, mallName):
        # proxyServerIndex 초기화ㄴ
        global proxyServerIndex
        proxyServerIndex = 0

        # 멀티쓰레드 생성
        # MAX_SEARCH_PAGE_SIZE 만큼 반복
        rankDtos = []
        with futures.ThreadPoolExecutor() as executor:
            for i in range(MAX_SEARCH_PAGE_SIZE):
                pageIndex = i + 1
                # proxy 이용해 naver ranking 조회
                searchPageResponse = executor.submit(NaverRankService.requestSearchPage, keyword, pageIndex)
                # 조회된 결과로 NaverRankDtos 추출
                rankDto = executor.submit(NaverRankService.searchCurrentPageRank, searchPageResponse.result(), mallName, pageIndex)
                rankDtos.append(rankDto)

        result = []
        for f in futures.as_completed(rankDtos):
            result.extend(f.result())

        return result
