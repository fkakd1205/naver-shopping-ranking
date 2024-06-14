from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import asyncio
import aiohttp

from aiohttp.client_exceptions import ClientProxyConnectionError, ClientOSError, ClientHttpProxyError

NAVER_NEWS_REQUEST_URL = "https://finance.naver.com/news/news_list.naver"
REQUEST_PAGE_SIZE = 2
TOTAL_REQUEST_TIMEOUT_SIZE = 15
CONTENTS_SIZE = 25

class AsyncTestService():
    
    async def get_page_response(self, pageIndex):
        response = None
        subjects = []
        headers = {"user-agent": UserAgent().random}
        params = {
            'mode': 'RANK',
            'page': pageIndex+1
        }

        try:
            async with aiohttp.ClientSession() as session:
                res = await session.get(
                    url=NAVER_NEWS_REQUEST_URL,
                    headers=headers,
                    params=params
                    )
                response = await res.text()
        except (ConnectionRefusedError, ClientProxyConnectionError, ClientOSError, ClientHttpProxyError):
            print("proxy connection error")
        except asyncio.TimeoutError:
            print("proxy connection time out")
        except aiohttp.ServerDisconnectedError:
            print("server does not accept request")

        try:
            dom = BeautifulSoup(response, "html.parser")
            articles = dom.select("#contentarea_left > div.hotNewsList._replaceNewsLink > ul > li > ul.simpleNewsList > li > a")
            for idx, article in enumerate(articles):
                subjects.append(f"{(pageIndex * CONTENTS_SIZE) + idx+1} : {article.string}")
        except (KeyError, AttributeError, UnboundLocalError, TypeError):
            # 응답은 넘어오지만, response attribute가 올바르지 않는다면 다음 프록시 요청
            print("response attribute error")
            
        return subjects
        
    async def start_test(self):
        req = [self.get_page_response(i) for i in range(REQUEST_PAGE_SIZE)]
        tasks = asyncio.gather(*req)
        results = []

        try:
            await asyncio.wait_for(tasks, timeout=TOTAL_REQUEST_TIMEOUT_SIZE)
        except asyncio.TimeoutError:
            tasks.cancel()
            raise TimeoutError("request time out")
        
        for result in tasks.result():
            results.extend(result)

        return results
        
        
    