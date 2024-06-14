from flask_restx import Namespace, Resource
from http import HTTPStatus
import asyncio

from domain.message.dto.MessageDto import MessageDto
from domain.async_test.service.AsyncTestService import AsyncTestService

AsyncTestApi = Namespace('AsyncTestApi')

@AsyncTestApi.route('', methods=['GET'])
class ProxyTest(Resource):
    def get(self):
        message = MessageDto()
        asyncTestService = AsyncTestService()
        message.setData(asyncio.run(asyncTestService.start_test()))
        message.setStatus(HTTPStatus.OK)
        message.setMessage("success")
        return message.__dict__, message.statusCode
    