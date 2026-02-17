"""Graph API client for MS365"""

import requests
from typing import Dict, List, Optional, Any
from .auth import GraphAuthenticator


class GraphClient:
    """Client for Microsoft Graph API"""

    def __init__(self, authenticator: GraphAuthenticator):
        """
        Initialize Graph API client
        
        Args:
            authenticator: GraphAuthenticator instance
        """
        self.authenticator = authenticator
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.beta_url = "https://graph.microsoft.com/beta"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        token = self.authenticator.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get(self, endpoint: str, use_beta: bool = False) -> Dict[str, Any]:
        """
        Make GET request to Graph API
        
        Args:
            endpoint: API endpoint (e.g., '/users')
            use_beta: Use beta endpoint instead of v1.0
            
        Returns:
            JSON response as dictionary
        """
        base = self.beta_url if use_beta else self.base_url
        url = f"{base}{endpoint}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_all_pages(self, endpoint: str, use_beta: bool = False) -> List[Dict[str, Any]]:
        """
        Get all pages of results from a paginated endpoint
        
        Args:
            endpoint: API endpoint
            use_beta: Use beta endpoint instead of v1.0
            
        Returns:
            List of all items from all pages
        """
        items = []
        base = self.beta_url if use_beta else self.base_url
        url = f"{base}{endpoint}"

        while url:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

            if "value" in data:
                items.extend(data["value"])
            else:
                items.append(data)

            url = data.get("@odata.nextLink")

        return items

    def post(
        self, endpoint: str, data: Dict[str, Any], use_beta: bool = False
    ) -> Dict[str, Any]:
        """
        Make POST request to Graph API
        
        Args:
            endpoint: API endpoint
            data: Request body
            use_beta: Use beta endpoint instead of v1.0
            
        Returns:
            JSON response as dictionary
        """
        base = self.beta_url if use_beta else self.base_url
        url = f"{base}{endpoint}"
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
