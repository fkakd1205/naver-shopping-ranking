from flask_restx import Api
from flask import Flask

from domain.naver_rank.controller.NaverRankApi import NaverRankApi

app = Flask(__name__)
api = Api(app)

api.add_namespace(NaverRankApi, "/api/v1/rank/naver")