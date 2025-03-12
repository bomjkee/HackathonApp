import pytest
from httpx import AsyncClient, Response

from tests.test_main import make_request


# GET запросы
@pytest.mark.asyncio
async def test_get_all_hackathons(async_client: AsyncClient):
    response: Response = await make_request(client=async_client, api_url="/hackathons")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_hackathon_by_id(async_client: AsyncClient):
    response: Response = await make_request(client=async_client, api_url="/hackathons/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1





# PUT запросы
# # 1. Редактирование команды -
# team_update = {
#     "name": "ferg",
#     "is_open": False,
#     "description": "Команда разработчиков серверных приложений"
# }
# await test_request_func("/teams/11", method="PUT", headers=front_headers, data=team_update)

# DELETE запросы
# # 1. Удаление команды +
# await test_request_func("/teams/16", method="DELETE", headers=front_headers)
# # 2. Выйти из команды -
# await test_request_func("/teams/1/leave", method="DELETE", headers=front_headers)


