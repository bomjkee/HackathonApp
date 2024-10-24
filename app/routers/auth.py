from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Request


from app.db.dao_models import UserDAO
from app.requests.user import RBUser
from app.responses.user import SUser
from app.responses.error import SError
from app.utils.dependencies import fast_auth_user

from config import logger


router = APIRouter(prefix='/auth', tags=['Работа с пользователями'])


@router.get("/", response_model=Union[SUser, SError])
async def get_user():
    user = await UserDAO.find_one_or_none(tg_id=id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user.to_dict()
