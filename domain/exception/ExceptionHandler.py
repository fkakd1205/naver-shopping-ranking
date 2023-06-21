import traceback
from http import HTTPStatus

from domain.exception.types.CustomException import CustomException
from domain.message.dto.MessageDto import MessageDto

def ExceptionHandler(app):
    message = MessageDto()
    
    @app.errorhandler(CustomException)
    def CustomExceptionHandler(e):
        # traceback.print_exc()
        message.setData(None)
        message.setStatus(HTTPStatus.BAD_REQUEST)
        message.setMessage(str(e))
        return message.__dict__, message.statusCode
    
    @app.errorhandler(TimeoutError)
    def TimeoutExceptionHandler(e):
        # traceback.print_exc()
        message.setData(None)
        message.setStatus(HTTPStatus.BAD_REQUEST)
        message.setMessage(str(e))
        return message.__dict__, message.statusCode

    # @app.errorhandler(Exception)
    # def CommonExceptionHandler(e):
    #     traceback.print_exc()
    #     message.setData(None)
    #     message.setStatus(HTTPStatus.BAD_REQUEST)
    #     message.setMessage(str(e))
    #     return message.__dict__, message.statusCode
