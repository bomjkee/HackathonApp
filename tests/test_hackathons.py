import pytest
from httpx import AsyncClient, Response

from tests.conftest import make_request


# GET запросы
@pytest.mark.asyncio
async def test_get_all_hackathons(async_client: AsyncClient):
    response: Response = await make_request(client=async_client, api_url="/hackathons")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_hackathon_by_id(async_client: AsyncClient):
    response: Response = await make_request(client=async_client, api_url="/hackathons/3")
    assert response.status_code == 200
    assert response.json()["id"] == 3






