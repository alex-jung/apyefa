import pytest
import requests


@pytest.fixture
def run_query(query_url):
    return requests.get(query_url).text
