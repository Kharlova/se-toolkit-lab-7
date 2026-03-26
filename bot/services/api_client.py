"""LMS API client with Bearer token authentication."""

import httpx
from typing import Optional
from config import load_config


class LMSAPIClient:
    """Client for LMS backend API."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize API client.
        
        Args:
            base_url: LMS API base URL (default from config)
            api_key: LMS API key for Bearer auth (default from config)
        """
        config = load_config()
        self.base_url = base_url or config["lms_api_base_url"]
        self.api_key = api_key or config["lms_api_key"]
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0
            )
        return self._client

    def get_items(self) -> list:
        """Get all items (labs and tasks).
        
        Returns:
            List of items from the backend.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        client = self._get_client()
        response = client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_analytics_pass_rates(self, lab: str) -> list:
        """Get pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., "lab-04")
            
        Returns:
            List of pass rate data.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        client = self._get_client()
        response = client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check backend health by fetching items.
        
        Returns:
            Dict with 'status' and 'item_count' keys.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        items = self.get_items()
        return {"status": "healthy", "item_count": len(items)}

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


# Global client instance (lazy initialization)
_api_client: Optional[LMSAPIClient] = None


def get_api_client() -> LMSAPIClient:
    """Get or create global API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = LMSAPIClient()
    return _api_client
