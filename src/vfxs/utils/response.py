
import typing

from fastapi import status
from fastapi.responses import JSONResponse

from .enums import ResponseCode


def jsonify(
        *,
        code: ResponseCode = ResponseCode.E0,
        message: str = 'success',
        data: typing.Any = None,
        status_code: int = 200
):
    content = {
        'code': code.value,
        'message': message,
        'data': data
    }
    return JSONResponse(content=content, status_code=status_code)


def response_200(data):
    return jsonify(data=data)


def response_400(message: str, code: ResponseCode = ResponseCode.E10000):
    return jsonify(code=code, message=message, status_code=status.HTTP_400_BAD_REQUEST)
