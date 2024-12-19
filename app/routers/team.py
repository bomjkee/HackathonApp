from sys import prefix
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request

from app.db.dao_models import UserDAO, TeamDAO, MemberDAO

from app.requests.hackathon import RBHackathon
from app.responses.team import STeam
from app.responses.error import SError
from app.utils.dependencies import exception_handler, fast_auth_user

router = APIRouter(prefix='/teams', tags=['Команды на хакатоне'])


@router.get('/', summary="Просмотреть все команды", response_model=List[STeam])
async def get_all_teams():
    teams = await TeamDAO.find_all_as_json()
    if teams is None:
        raise HTTPException(status_code=404, detail="В текущее время хакатонов нет")
    else:
        return teams


@router.get('/{id}', response_model=STeam)
async def get_team(team_id: int):
    team = await TeamDAO.find_one_or_none(id=team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    members = await MemberDAO.find_all(team_id=team_id)
    member_dicts = []
    for member in members:
        user = await UserDAO.find_one_or_none(tg_id=member.user_id)
        if user:
            member_dict = member.to_dict()
            member_dict['username'] = user.username
            member_dicts.append(member_dict)

    team_dict = team.to_dict()
    team_dict['members'] = member_dicts

    return team_dict
