from flask_restx import Api
from flask import Flask
from flask_cors import CORS
import urllib3

from domain.naver_rank.controller.NaverRankApi import NaverRankApi
from domain.test.TestApi import TestApi
from domain.proxy_test.controller.ProxyTestApi import ProxyTestApi
from domain.async_test.controller.AsyncTestApi import AsyncTestApi

from exception.ExceptionHandler import ExceptionHandler

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
api = Api(app)
CORS(
    app,
    supports_credentials=True
)

api.add_namespace(NaverRankApi, "/api/v1/rank/naver")
api.add_namespace(TestApi, "/api/v1/test")
api.add_namespace(ProxyTestApi, "/api/v1/proxy")
api.add_namespace(AsyncTestApi, "/api/v1/async")

ExceptionHandler(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)