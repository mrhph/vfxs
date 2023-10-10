
import typing

from fastapi.responses import JSONResponse

from .enums import ResponseCode


def jsonify(data: typing.Any):
    return JSONResponse(content=data)


def error_jsonify(message: str, code: ResponseCode = ResponseCode.E10000, status_code: int = 400):
    data = {'code': code.value, 'message': message}
    return JSONResponse(content=data, status_code=status_code)
