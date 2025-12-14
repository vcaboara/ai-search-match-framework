"""
Base provider interface for data sources.

All providers should implement this interface to ensure consistent
behavior across different data sources.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for all data source providers.

    Providers fetch data from various sources (APIs, web scraping, MCPs)
    and return standardized result dictionaries.
    """

    def __init__(self, name: str, enabled: bool = True):
        """
        Initialize provider.

        Args:
            name: Provider identifier
            enabled: Whether provider is active
        """
        self.name = name
        self.enabled = enabled
        self._results_cache = {}

    @abstractmethod
    def search(self, query: str, count: int = 10, **kwargs) -> List[Dict]:
        """
        Execute search query.

        Args:
            query: Search terms
            count: Maximum results to return
            **kwargs: Provider-specific parameters

        Returns:
            List of standardized result dictionaries with keys:
                - id: Unique identifier
                - title: Result title
                - description: Result description
                - link: URL to result
                - source: Provider name
                - timestamp: When found
                - metadata: Provider-specific data
        """
        pass

    def validate(self, item: Dict) -> bool:
        """
        Validate item meets quality standards.

        Args:
            item: Result dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["id", "title", "link"]
        return all(field in item and item[field] for field in required_fields)

    def normalize(self, raw_item: Dict) -> Dict:
        """
        Convert provider-specific format to standard format.

        Args:
            raw_item: Raw result from provider

        Returns:
            Standardized result dictionary
        """
        return {
            "id": str(raw_item.get("id", "")),
            "title": raw_item.get("title", ""),
            "description": raw_item.get("description", ""),
            "link": raw_item.get("link", ""),
            "source": self.name,
            "timestamp": raw_item.get("timestamp"),
            "metadata": raw_item.get("metadata", {})
        }

    def is_enabled(self) -> bool:
        """Check if provider is enabled."""
        return self.enabled

    def cache_results(self, query: str, results: List[Dict], ttl_seconds: int = 300):
        """
        Cache search results.

        Args:
            query: Query string used as cache key
            results: Results to cache
            ttl_seconds: Time to live in seconds
        """
        from datetime import datetime, timedelta
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self._results_cache[query] = (results, expiry)

    def get_cached_results(self, query: str) -> Optional[List[Dict]]:
        """
        Retrieve cached results if still valid.

        Args:
            query: Query string

        Returns:
            Cached results or None if expired/missing
        """
        if query not in self._results_cache:
            return None

        from datetime import datetime
        results, expiry = self._results_cache[query]
        if datetime.now() > expiry:
            del self._results_cache[query]
            return None

        return results


class APIProvider(BaseProvider):
    """Base class for REST API providers."""

    def __init__(self, name: str, api_key: str, base_url: str, enabled: bool = True):
        """
        Initialize API provider.

        Args:
            name: Provider identifier
            api_key: API authentication key
            base_url: Base URL for API endpoints
            enabled: Whether provider is active
        """
        super().__init__(name, enabled)
        self.api_key = api_key
        self.base_url = base_url
        self._session = None

    def get_session(self):
        """Get or create requests session with headers."""
        if self._session is None:
            import requests
            self._session = requests.Session()
            self._session.headers.update(self.get_headers())
        return self._session

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def handle_rate_limit(self, response):
        """Handle rate limit errors."""
        import time
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(f"{self.name} rate limited, waiting {retry_after}s")
            time.sleep(retry_after)
            return True
        return False


class MCPProvider(BaseProvider):
    """Base class for Model Context Protocol providers."""

    def __init__(self, name: str, server_name: str, enabled: bool = True):
        """
        Initialize MCP provider.

        Args:
            name: Provider identifier
            server_name: MCP server name
            enabled: Whether provider is active
        """
        super().__init__(name, enabled)
        self.server_name = server_name

    @abstractmethod
    def get_mcp_tool(self, tool_name: str):
        """
        Get MCP tool by name.

        Args:
            tool_name: Tool identifier

        Returns:
            Tool callable
        """
        pass
