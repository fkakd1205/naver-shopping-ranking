import requests
from bs4 import BeautifulSoup
import json

from domain.naver_rank.dto.NaverRankDto import NaverRankDto

DEFAULT_PAGINGSIZE = 80

class NaverRankService():
    def searchRank(keyword, mallName):
        pageIndex = 2

        url = ("https://search.shopping.naver.com/search/all"
        f"?query={keyword}"
        f"&frm=NVSCPRO"
        f"&pagingIndex={pageIndex}"
        f"&pagingSize={DEFAULT_PAGINGSIZE}")

        print(url)
        response = requests.get(url)

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
                        dto.setPrice(item['price'])
                        break
        
            if dto.rank != 0: 
                result.append(dto.__dict__)
    
        return result