import time
import json
import urllib
import hmac
import hashlib

from fastapi.exceptions import RequestValidationError
from loguru import logger
from functools import wraps
from datetime import timedelta
from urllib.parse import unquote
from fastapi import HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing import Dict, Tuple, Type

from app.api.typization.responses import T, SUser, ErrorResponse, Error
from config import settings


def reformat_data(query_string: str) -> Dict:
    parsed_qs = urllib.parse.parse_qs(query_string)

    parsed_dict = {}
    for key, value in parsed_qs.items():
        if len(value) == 1:
            parsed_dict[key] = value[0]
        else:
            parsed_dict[key] = value

    if 'user' in parsed_dict:
        parsed_dict['user'] = json.loads(parsed_dict['user'])

    return parsed_dict


def eligible_checker(hash_str: str, init_data: str, token=settings.BOT_TOKEN, c_str: str = "WebAppData") -> bool:
    init_data = sorted([chunk.split("=")
                        for chunk in unquote(init_data).split("&")
                        if chunk[:len("hash=")] != "hash="],
                       key=lambda x: x[0])
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    secret_key = hmac.new(c_str.encode(), token.encode(),
                          hashlib.sha256).digest()
    data_check = hmac.new(secret_key, init_data.encode(),
                          hashlib.sha256)

    return data_check.hexdigest() == hash_str


def parse_query_string(query_string: str) -> Dict:
    parts = query_string.split('&')
    result = {}

    for part in parts:
        key, value = part.split('=', 1)
        if key == 'user':
            result[key] = json.loads(urllib.parse.unquote(value))
        else:
            result[key] = urllib.parse.unquote(value)

    return result


async def authorization_check(headers: dict) -> Tuple[bool, Dict | None]:
    """ Проверка авторизации пользователя """

    if "authorization" in headers and "tma " in headers['authorization']:
        query_data = headers["authorization"].replace("tma ", "")
        dict_data = parse_query_string(query_data)
        valid_status = eligible_checker(query_data.split("hash=")[-1], query_data)
        logger.info(
            f"{valid_status} | {((time.time() - int(dict_data['auth_date'])) <= timedelta(hours=2000).total_seconds())}")
        if valid_status and ((time.time() - int(dict_data['auth_date'])) <= timedelta(hours=2000).total_seconds()):
            dict_data = reformat_data(query_data)
            return True, dict_data

    return False, None


def exception_handler(f):
    """ Обработчик исключений """

    @wraps(f)
    async def decorated_function(*args, **kwargs):
        try:
            return await f(*args, **kwargs)

        except RequestValidationError as e:
            logger.warning(f"RequestValidationError в функции: {f.__name__} with args: {args} and\n"
                           f"kwargs: {kwargs}\n - {e.errors()}")
            error_messages = [
                f"{err['loc'][-1]}: {err['msg']}" for err in e.errors()
            ]
            error = Error(code="VALIDATION_ERROR", message=", ".join(error_messages))
            error_response = ErrorResponse(status="error", data=error)
            return JSONResponse(
                status_code=422,
                content=error_response.model_dump(),
            )

        except HTTPException as e:
            logger.warning(
                f"HTTPException в функции: {f.__name__} with args: {args} and\n"
                f"kwargs: {kwargs}\n - {e.detail} (status_code: {e.status_code})"
            )

            error = Error(code=f"HTTP_{e.status_code}", message=e.detail)
            error_response = ErrorResponse(status="error", data=error)

            return JSONResponse(
                status_code=e.status_code, content=error_response.model_dump()
            )

        except Exception as e:
            logger.error(
                f"Неизвестная ошибка в функции: {f.__name__} with args: {args} and\n"
                f"kwargs: {kwargs}\n - {e}"
            )
            error = Error(code="INTERNAL_SERVER_ERROR", message=str(e))
            error_response = ErrorResponse(status="error", data=error)

            return JSONResponse(status_code=500, content=error_response.model_dump(), )

    return decorated_function


def check_registration_for_app(user: SUser):
    return bool(user.full_name not in ["", " ", "<null>", None])


def generate_response_model(description: str = "Внутренняя ошибка сервера", model: Type[T] = ErrorResponse) -> dict:
    return {"model": model, "description": description}
