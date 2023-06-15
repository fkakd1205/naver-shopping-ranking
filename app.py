from flask_restx import Api
from flask import Flask
from flask_cors import CORS

from domain.naver_rank.controller.NaverRankApi import NaverRankApi
from domain.exception.ExceptionHandler import ExceptionHandler

app = Flask(__name__)
api = Api(app)
CORS(
    app,
    supports_credentials=True
)

api.add_namespace(NaverRankApi, "/api/v1/rank/naver")

ExceptionHandler(api)
