import pytest
from httpx import AsyncClient, Response

from tests.conftest import make_request


# POST запросы
@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient, authorization_headers: dict):
    user_update = {
        "full_name": "Малахов Андрей Викторович",
        "is_mirea_student": True,
        "group": "ББББ-01-22"
    }
    response: Response = await make_request(client=async_client, api_url="/register",
                                            method="POST", headers=authorization_headers,
                                  data=user_update)
    assert response.status_code == 200
    assert response.json()["status"] == "success"



# GET запросы
@pytest.mark.asyncio
async def test_get_my_profile(async_client: AsyncClient, authorization_headers: dict):
    response: Response = await make_request(client=async_client, api_url="/my_profile", headers=authorization_headers)
    assert response.status_code == 200
    assert response.json()["user"]


@pytest.mark.asyncio
async def test_check_registration(async_client: AsyncClient, authorization_headers: dict):
    response: Response = await make_request(client=async_client, api_url="/register", headers=authorization_headers)
    assert response.status_code == 200
    assert response.json()["is_registered"]

