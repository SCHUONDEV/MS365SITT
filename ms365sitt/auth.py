"""Authentication module for MS365 Graph API"""

import msal
import os
from typing import Optional, Dict


class GraphAuthenticator:
    """Handle authentication to Microsoft Graph API"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        authority: Optional[str] = None,
    ):
        """
        Initialize Graph API authenticator
        
        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID
            authority: Optional authority URL (defaults to public cloud)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = authority or f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self._token = None

    def get_token(self) -> str:
        """
        Get access token for Graph API
        
        Returns:
            Access token string
            
        Raises:
            Exception: If authentication fails
        """
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )

        result = app.acquire_token_silent(self.scope, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=self.scope)

        if "access_token" in result:
            self._token = result["access_token"]
            return self._token
        else:
            error = result.get("error", "Unknown error")
            error_desc = result.get("error_description", "No description")
            raise Exception(f"Authentication failed: {error} - {error_desc}")

    @classmethod
    def from_env(cls) -> "GraphAuthenticator":
        """
        Create authenticator from environment variables
        
        Expected environment variables:
            - AZURE_CLIENT_ID
            - AZURE_CLIENT_SECRET
            - AZURE_TENANT_ID
            
        Returns:
            GraphAuthenticator instance
        """
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")

        if not all([client_id, client_secret, tenant_id]):
            raise ValueError(
                "Missing required environment variables: "
                "AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID"
            )

        return cls(client_id, client_secret, tenant_id)
