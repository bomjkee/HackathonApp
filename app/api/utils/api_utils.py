import time
import json
import urllib
import hmac
import hashlib
from loguru import logger
from functools import wraps
from datetime import timedelta
from urllib.parse import unquote
from typing import Dict, Union
from fastapi.requests import Request
from fastapi import HTTPException

from app.api.typization.schemas import TelegramIDModel
from app.api.typization.exceptions import AuthException
from app.api.utils.redis_operations import redis_data
from app.db.session_maker import db
from app.db.dao import UserDAO
from config import settings




def reformat_data(query_string: str) -> dict:
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


def eligible_checker(hash_str, init_data, token=settings.BOT_TOKEN, c_str="WebAppData") -> bool:
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


def parse_query_string(query_string: str) -> dict:
    parts = query_string.split('&')
    result = {}

    for part in parts:
        key, value = part.split('=', 1)
        if key == 'user':
            result[key] = json.loads(urllib.parse.unquote(value))
        else:
            result[key] = urllib.parse.unquote(value)

    return result


async def authorization_check(headers: dict) -> (bool, dict | None):
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
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in function: {f.__name__} with args: {args} and\n"
                         f"kwargs: {kwargs}\n  - {e}")
            raise HTTPException(status_code=404, detail={"result": "Error", "data": "Logs"})
    return decorated_function