from flask_restx import Namespace, Resource
from http import HTTPStatus
from flask import request
import time
import asyncio

from domain.message.dto.MessageDto import MessageDto
from domain.naver_rank.service.NaverRankServiceV6 import NaverRankService

NaverRankApi = Namespace('NaverRankApi')

@NaverRankApi.route('', methods=['GET'])
class NaverRank(Resource):
    def get(self):
        message = MessageDto()

        keyword = request.args.get("keyword", default="", type=str)
        mallName = request.args.get("mallName", default="", type=str)

        # 파라미터로 넘어온 검색값이 공백인 경우
        if(keyword == "" or mallName == ""):
            message.setData(None)
            message.setStatus(HTTPStatus.OK)
            message.setMessage("no_contents")
            return message.__dict__, message.statusCode

        start = time.perf_counter()
        naverRankService = NaverRankService(keyword, mallName)
        message.setData(asyncio.run(naverRankService.searchRank()))
        message.setStatus(HTTPStatus.OK)
        message.setMessage("success")
        finish = time.perf_counter()

        print(f"api 응답완료 : {finish - start}")
        return message.__dict__, message.statusCode
    