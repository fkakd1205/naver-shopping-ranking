import traceback
from http import HTTPStatus

from exception.types.CustomException import CustomException
from domain.message.dto.MessageDto import MessageDto

def ExceptionHandler(app):
    message = MessageDto()
    
    @app.errorhandler(CustomException)
    def CustomExceptionHandler(e):
        message.setData(None)
        message.setStatus(HTTPStatus.BAD_REQUEST)
        message.setMessage(str(e))
        return message.__dict__, message.statusCode
    
    @app.errorhandler(TimeoutError)
    def TimeoutExceptionHandler(e):
        message.setData(None)
        message.setStatus(HTTPStatus.REQUEST_TIMEOUT)
        message.setMessage(str(e))
        return message.__dict__, message.statusCode
