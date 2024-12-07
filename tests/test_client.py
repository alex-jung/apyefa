import pytest

from apyefa.client import EfaClient
from apyefa.data_classes import SystemInfo


@pytest.fixture
async def test_async_client():
    async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
        yield client


async def test_info(test_async_client: EfaClient):
    result = await test_async_client.info()

    assert result is not None
    assert isinstance(result, SystemInfo)
