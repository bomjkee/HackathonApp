from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.routers.user import get_user
from app.routers.hackathon import get_hackathon
from app.routers.team import get_team, get_all_teams

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


@router.get('/', summary="Домашняя страница")
async def home_page(request: Request):
    return templates.TemplateResponse(name='home.html', context={'request': request, 'title': 'Домашняя страница'})


@router.get('/reg', summary="Регистрация")
async def reg_page(request: Request):
    return templates.TemplateResponse(name='reg-form.html', context={'request': request, 'title': 'Регистрация'})


@router.get('/profile', summary="Профиль")
async def profile_page(request: Request, user=Depends(get_user)):
    return templates.TemplateResponse(name='profile.html', context={'request': request, 'user': user,
                                                                      'title': 'Профиль'})

@router.get('/hackathon', summary="Хакатон")
async def hackathon_page(request: Request, hackathon=Depends(get_hackathon)):
    return templates.TemplateResponse(name='hackathon.html', context={'request': request, 'hackathon': hackathon, 'title': 'Хакатон'})


@router.get('/teams', summary="Команды")
async def teams_page(request: Request, teams=Depends(get_all_teams)):
    return templates.TemplateResponse(name='teams.html', context={'request': request, 'teams': teams, 'title': 'Команды'})

@router.get('/team/{id}', summary="Команда по id")
async def team_page(request: Request, team=Depends(get_team)):
    return templates.TemplateResponse(name='team.html', context={'request': request, 'team': team, 'title': 'Команда'})