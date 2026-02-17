"""Tests for authentication module"""

import pytest
from unittest.mock import Mock, patch
from ms365sitt.auth import GraphAuthenticator


def test_graph_authenticator_init():
    """Test GraphAuthenticator initialization"""
    auth = GraphAuthenticator(
        client_id="test-client-id",
        client_secret="test-secret",
        tenant_id="test-tenant-id",
    )

    assert auth.client_id == "test-client-id"
    assert auth.client_secret == "test-secret"
    assert auth.tenant_id == "test-tenant-id"
    assert "test-tenant-id" in auth.authority


@patch("ms365sitt.auth.msal.ConfidentialClientApplication")
def test_get_token_success(mock_msal):
    """Test successful token acquisition"""
    # Setup mock
    mock_app = Mock()
    mock_app.acquire_token_silent.return_value = None
    mock_app.acquire_token_for_client.return_value = {"access_token": "test-token"}
    mock_msal.return_value = mock_app

    auth = GraphAuthenticator(
        client_id="test-client-id",
        client_secret="test-secret",
        tenant_id="test-tenant-id",
    )

    token = auth.get_token()

    assert token == "test-token"
    assert auth._token == "test-token"


@patch("ms365sitt.auth.msal.ConfidentialClientApplication")
def test_get_token_failure(mock_msal):
    """Test token acquisition failure"""
    # Setup mock
    mock_app = Mock()
    mock_app.acquire_token_silent.return_value = None
    mock_app.acquire_token_for_client.return_value = {
        "error": "invalid_client",
        "error_description": "Invalid client",
    }
    mock_msal.return_value = mock_app

    auth = GraphAuthenticator(
        client_id="test-client-id",
        client_secret="test-secret",
        tenant_id="test-tenant-id",
    )

    with pytest.raises(Exception, match="Authentication failed"):
        auth.get_token()


@patch.dict(
    "os.environ",
    {
        "AZURE_CLIENT_ID": "env-client-id",
        "AZURE_CLIENT_SECRET": "env-secret",
        "AZURE_TENANT_ID": "env-tenant-id",
    },
)
def test_from_env_success():
    """Test creating authenticator from environment variables"""
    auth = GraphAuthenticator.from_env()

    assert auth.client_id == "env-client-id"
    assert auth.client_secret == "env-secret"
    assert auth.tenant_id == "env-tenant-id"


@patch.dict("os.environ", {}, clear=True)
def test_from_env_missing_vars():
    """Test from_env with missing environment variables"""
    with pytest.raises(ValueError, match="Missing required environment variables"):
        GraphAuthenticator.from_env()
