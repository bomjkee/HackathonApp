import pytest
from httpx import AsyncClient, Response

from tests.conftest import make_request



# GET запросы
@pytest.mark.asyncio
async def test_get_all_teams(async_client: AsyncClient):
    response: Response = await make_request(client=async_client, api_url="/teams")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_team_by_id(async_client: AsyncClient):
    response: Response = await make_request(client=async_client, api_url="/teams/1")
    assert response.status_code == 200
    assert response.json()["team"]["id"] == 1



# POST запросы
@pytest.mark.asyncio
async def test_create_team(async_client: AsyncClient, authorization_headers: dict):
    team_create = {
        "name": "Olsos",
        "is_open": True,
        "description": "Команда разработчиков корпоративных приложений",
        "hackathon_id": 1
    }
    response: Response = await make_request(client=async_client, api_url="/teams",
                                            method="POST", headers=authorization_headers, data=team_create)
    assert response.status_code == 200
    assert response.json()["status"] == "Success"


@pytest.mark.asyncio
async def test_invite_user_to_team(async_client: AsyncClient, authorization_headers: dict):
    invite_create = {
        "team_id": 1,
        "invite_user_id": 741185494
    }
    response: Response = await make_request(client=async_client, api_url="/teams/invite",
                                            method="POST", headers=authorization_headers, data=invite_create)
    assert response.status_code == 200
    assert response.json()["status"] == "Success"


@pytest.mark.asyncio
async def test_join_to_team(async_client: AsyncClient, authorization_headers: dict):
    response: Response = await make_request(client=async_client, api_url="/teams/3/join",
                                            method="POST", headers=authorization_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Success"



# PATCH запросы
@pytest.mark.asyncio
async def test_update_team(async_client: AsyncClient, authorization_headers: dict):
    team_update = {
        "name": "Olso",
        "is_open": True,
        "description": "Команда разработчиков корпоративных приложений"
    }
    response: Response = await make_request(client=async_client, api_url="/teams/24",
                                            method="PATCH", headers=authorization_headers, data=team_update)
    assert response.status_code == 200
    assert response.json()["status"] == "Success"



# DELETE запросы
@pytest.mark.asyncio
async def test_leave_team(async_client: AsyncClient, authorization_headers: dict):
    response: Response = await make_request(client=async_client, api_url="/teams/25/leave",
                                            method="DELETE", headers=authorization_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Success"


@pytest.mark.asyncio
async def test_delete_team(async_client: AsyncClient, authorization_headers: dict):
    response: Response = await make_request(client=async_client, api_url="/teams/25",
                                            method="DELETE", headers=authorization_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Success"