from flask_restx import Api
from flask import Flask
from flask_cors import CORS

from domain.naver_rank.controller.NaverRankApi import NaverRankApi
from domain.test.TestApi import TestApi
from domain.exception.ExceptionHandler import ExceptionHandler

app = Flask(__name__)
api = Api(app)
CORS(
    app,
    supports_credentials=True
)

api.add_namespace(NaverRankApi, "/api/v1/rank/naver")
api.add_namespace(TestApi, "/api/v1/test")

ExceptionHandler(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)