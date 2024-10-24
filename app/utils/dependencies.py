import time
import json
import urllib
import traceback
from functools import wraps

import hmac
import hashlib
from urllib.parse import unquote
from fastapi.responses import JSONResponse
from fastapi import Request

from app.db.dao_models import UserDAO
from config import bot_token, logger



async def fast_auth_user(request: Request):

    headers = dict(request.headers)

    authorization_status, dict_data = await authorization_check(headers)

    if authorization_status:
        user = await UserDAO.find_one_or_none(tg_id=dict_data["user"]["id"])
        if user is not None:
            return dict_data, user.model_dump_json()
        else:
            return JSONResponse(content={"result": "Error", "data": "User not found"}, status_code=400)
    else:
        return JSONResponse(content={"result": "Error", "data": "Authorization Error"}, status_code=400)



async def authorization_check(headers: dict) -> (bool, dict | None):

    if "authorization" in headers and "tma " in headers['authorization']:

        query_data = headers["authorization"].replace("tma ", "")
        dict_data = parse_query_string(query_data)
        valid_status = eligible_checker(query_data.split("hash=")[-1], query_data)

        logger.info(f"{valid_status} | {((time.time() - int(dict_data['auth_date']))) <= 500*60*60}")

        if valid_status and ((time.time() - int(dict_data['auth_date'])) <= 500*60*60):
            dict_data = reformat_data(query_data)
            return True, dict_data

    return False, None


def eligible_checker(hash_str, init_data, token=bot_token, c_str="WebAppData"):
    init_data = sorted([chunk.split("=")
                        for chunk in unquote(init_data).split("&")
                        if chunk[:len("hash=")] != "hash="], key=lambda x: x[0])
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()

    data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

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


def exception_handler(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except:
            traceback.print_exc()
            return JSONResponse(content={"result": "Error", "data": "Logs"}, status_code=499)
    return decorated_function