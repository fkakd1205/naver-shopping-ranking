from datetime import datetime
from http import HTTPStatus

class MessageDto():
    def __init__(self):
        self.status = HTTPStatus.BAD_REQUEST.phrase
        self.statusCode = HTTPStatus.BAD_REQUEST.value
        self.statusMessage = HTTPStatus.BAD_REQUEST.phrase
        self.message = None
        self.memo = None
        self.data = None
        self.datetime = str(datetime.now())

    def setStatus(self, status):
        self.status = status.phrase
        self.statusCode = status.value
        self.statusMessage = status.phrase

    def setData(self, data):
        self.data = data

    def setMessage(self, message):
        self.message = message

    def setMemo(self, memo):
        self.memo = memo
        