from flask_restx import Namespace, Resource
from http import HTTPStatus
from flask import request
import asyncio

from domain.message.dto.MessageDto import MessageDto
from domain.proxy_test.service.ProxyTestService import ProxyTestService

ProxyTestApi = Namespace('ProxyTestApi')

@ProxyTestApi.route('', methods=['GET'])
class ProxyTest(Resource):
    def get(self):
        message = MessageDto()

        keyword = request.args.get("keyword", default="", type=str)
        mallName = request.args.get("mallName", default="", type=str)
        pageSize = 1

        # 파라미터로 넘어온 검색값이 공백인 경우
        if(keyword == "" or mallName == ""):
            message.setData(None)
            message.setStatus(HTTPStatus.OK)
            message.setMessage("no_contents")
            return message.__dict__, message.statusCode

        proxyTestService = ProxyTestService(keyword, mallName, pageSize)
        # message.setData(asyncio.run(proxyTestService.search_rank()))
        message.setData(proxyTestService.search_rank())
        message.setStatus(HTTPStatus.OK)
        message.setMessage("success")
        return message.__dict__, message.statusCode
    