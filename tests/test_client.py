"""Tests for Graph API client"""

import pytest
from unittest.mock import Mock, patch
from ms365sitt.client import GraphClient
from ms365sitt.auth import GraphAuthenticator


@pytest.fixture
def mock_authenticator():
    """Create mock authenticator"""
    auth = Mock(spec=GraphAuthenticator)
    auth.get_token.return_value = "test-token"
    return auth


@pytest.fixture
def client(mock_authenticator):
    """Create GraphClient with mock authenticator"""
    return GraphClient(mock_authenticator)


def test_client_init(mock_authenticator):
    """Test GraphClient initialization"""
    client = GraphClient(mock_authenticator)
    assert client.authenticator == mock_authenticator
    assert "graph.microsoft.com" in client.base_url


def test_get_headers(client):
    """Test header generation"""
    headers = client._get_headers()

    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Content-Type"] == "application/json"


@patch("ms365sitt.client.requests.get")
def test_get_request(mock_get, client):
    """Test GET request"""
    mock_response = Mock()
    mock_response.json.return_value = {"value": "test"}
    mock_get.return_value = mock_response

    result = client.get("/test/endpoint")

    assert result == {"value": "test"}
    mock_get.assert_called_once()


@patch("ms365sitt.client.requests.get")
def test_get_all_pages(mock_get, client):
    """Test paginated GET request"""
    # First page
    mock_response1 = Mock()
    mock_response1.json.return_value = {
        "value": [{"id": 1}, {"id": 2}],
        "@odata.nextLink": "https://graph.microsoft.com/v1.0/test?$skip=2",
    }

    # Second page
    mock_response2 = Mock()
    mock_response2.json.return_value = {"value": [{"id": 3}, {"id": 4}]}

    mock_get.side_effect = [mock_response1, mock_response2]

    result = client.get_all_pages("/test")

    assert len(result) == 4
    assert result[0]["id"] == 1
    assert result[3]["id"] == 4
    assert mock_get.call_count == 2
