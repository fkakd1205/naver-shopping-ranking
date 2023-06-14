import requests
from bs4 import BeautifulSoup
import json
import time
from concurrent import futures

from domain.naver_rank.dto.NaverRankDto import NaverRankDto
from domain.exception.types.CustomException import CustomException

DEFAULT_PAGINGSIZE = 80

class NaverRankService():
    def searchCurrentPageRank(keyword, mallName, pageIndex):
        try:
            url = ("https://search.shopping.naver.com/search/all"
            f"?query={keyword}"
            f"&frm=NVSCPRO"
            f"&pagingIndex={pageIndex}"
            f"&pagingSize={DEFAULT_PAGINGSIZE}")

            response = requests.get(url)

            if(response.status_code !=  200):
                raise Exception("api request error.")

            dom = BeautifulSoup(response.text, "html.parser")
            type(dom)

            resultObj = dom.select_one("#__NEXT_DATA__").text
            productJsonObj = json.loads(resultObj)
            productList = productJsonObj['props']['pageProps']['initialState']['products']['list']

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
        # 10페이지 검색 가능
        with futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(NaverRankService.searchCurrentPageRank, keyword, mallName, i+1) for i in range(10)]

        result = []
        for f in futures.as_completed(results):
            result.extend(f.result())

        return result


        