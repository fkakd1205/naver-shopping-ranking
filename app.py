from flask import Flask
app = Flask(__name__)
import requests
from bs4 import BeautifulSoup

# @app.route('/')
# def hello_world():
#     return 'hello'

@app.route('/')
def search_rank():
    keyword="고양이 장난감"
    
    url = f"https://search.shopping.naver.com/search/all?query={keyword}&bt=-1&frm=NVSCPRO"
    response = requests.get(url)
    print(response)

    dom = BeautifulSoup(response.text, "html.parser")
    type(dom)

    elements = dom.select("#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div")
    print(len(elements))

    items = []
    for element in elements:
        productName = element.select_one(".adProduct_info_area__dTSZf > div.adProduct_title__amInq > a")
        storeName = element.select_one(".adProduct_mall_area__H952t > div.adProduct_mall_title__kk0Tr > a.adProduct_mall__zeLIC")

        if (productName is None ) :
            productName = element.select_one(".product_info_area__xxCTi > .product_title__Mmw2K > a")

        if (storeName is None) : 
            storeName = element.select_one(".product_mall_area___f3wo > .product_mall_title__Xer1m > a")
            if(storeName.text == "쇼핑몰별 최저가") :
                storeNames = element.select(".product_mall_area___f3wo > .product_mall_list__RU42O > li > .product_mall_item__KUMTJ")

                for store in storeNames:
                    name = store.select_one(".product_mall_info__iWlJ5 > .product_mall_name__MbUf3")
                    storeName.append(name)

        print(productName.text)
        print(storeName.text)

        data = {
              "productName" : productName.text,
              "storeName" : storeName.text,
            #   "isAdvertising" : 
        }
        items.append(data)

    return items