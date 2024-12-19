from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Request

from app.db.dao_models import UserDAO, HackathonDAO
from app.requests.hackathon import RBHackathon
from app.responses.hackathon import SHackathon
from app.responses.error import SError
from app.utils.dependencies import exception_handler, fast_auth_user

router = APIRouter(tags=['Просмотр хакатонов'])

@router.get('/', response_model=SHackathon)
async def get_hackathon():
    hackathon = await HackathonDAO.find_one_or_none(id=1)
    if hackathon is None:
        raise HTTPException(status_code=404, detail="Хакатон не найден")
    return hackathon.to_dict()




