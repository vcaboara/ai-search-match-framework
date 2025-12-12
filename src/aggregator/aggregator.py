"""
Aggregator for combining results from multiple providers.

Handles deduplication, sorting, and provider coordination.
"""
import logging
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Aggregator:
    """
    Coordinate multiple providers and aggregate results.
    
    Features:
    - Multi-provider search
    - Deduplication (URL-based and content hash)
    - Result sorting and filtering
    - Provider weighting
    """
    
    def __init__(self, providers: List, blocked_entities: Optional[List[Dict]] = None):
        """
        Initialize aggregator.
        
        Args:
            providers: List of BaseProvider instances
            blocked_entities: List of blocked sites/companies
        """
        self.providers = [p for p in providers if p.is_enabled()]
        self.blocked_entities = blocked_entities or []
        self._seen_urls = set()
        self._seen_hashes = set()
    
    def search(
        self,
        query: str,
        count: int = 10,
        deduplicate: bool = True,
        sort_by: Optional[str] = None
    ) -> List[Dict]:
        """
        Search across all providers.
        
        Args:
            query: Search terms
            count: Maximum results
            deduplicate: Remove duplicates
            sort_by: Field to sort by (optional)
            
        Returns:
            Aggregated and filtered results
        """
        all_results = []
        
        for provider in self.providers:
            try:
                logger.info(f"Searching {provider.name}...")
                results = provider.search(query, count=count)
                
                # Validate and normalize
                for item in results:
                    if provider.validate(item):
                        normalized = provider.normalize(item)
                        all_results.append(normalized)
                    else:
                        logger.debug(f"Invalid item from {provider.name}: {item}")
                
            except Exception as e:
                logger.error(f"{provider.name} search failed: {e}")
                continue
        
        # Apply filters
        filtered = self._filter_blocked(all_results)
        
        if deduplicate:
            filtered = self._deduplicate(filtered)
        
        if sort_by:
            filtered = self._sort_results(filtered, sort_by)
        
        return filtered[:count]
    
    def _filter_blocked(self, items: List[Dict]) -> List[Dict]:
        """Remove blocked entities."""
        filtered = []
        
        for item in items:
            if self._is_blocked(item):
                logger.debug(f"Blocked: {item.get('title', 'Unknown')}")
                continue
            filtered.append(item)
        
        return filtered
    
    def _is_blocked(self, item: Dict) -> bool:
        """Check if item matches block list."""
        for block in self.blocked_entities:
            block_type = block.get("type")
            block_value = block.get("value", "").lower()
            
            if block_type == "site":
                if block_value in item.get("link", "").lower():
                    return True
            
            elif block_type == "employer":
                company = item.get("metadata", {}).get("company", "").lower()
                if block_value in company:
                    return True
            
            elif block_type == "keyword":
                title = item.get("title", "").lower()
                desc = item.get("description", "").lower()
                if block_value in title or block_value in desc:
                    return True
        
        return False
    
    def _deduplicate(self, items: List[Dict]) -> List[Dict]:
        """
        Remove duplicate items.
        
        Uses URL matching and content hashing.
        """
        unique = []
        seen_urls = set()
        seen_hashes = set()
        
        for item in items:
            # Check URL
            url = item.get("link", "")
            if url and url in seen_urls:
                logger.debug(f"Duplicate URL: {url}")
                continue
            
            # Check content hash
            content_hash = self._hash_content(item)
            if content_hash in seen_hashes:
                logger.debug(f"Duplicate content: {item.get('title')}")
                continue
            
            seen_urls.add(url)
            seen_hashes.add(content_hash)
            unique.append(item)
        
        return unique
    
    def _hash_content(self, item: Dict) -> str:
        """Generate content hash for deduplication."""
        # Use title + description for similarity
        content = f"{item.get('title', '')}|{item.get('description', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _sort_results(self, items: List[Dict], sort_by: str) -> List[Dict]:
        """Sort results by field."""
        reverse = True  # Default to descending
        
        if sort_by.startswith("-"):
            sort_by = sort_by[1:]
            reverse = False
        
        try:
            return sorted(
                items,
                key=lambda x: x.get(sort_by, ""),
                reverse=reverse
            )
        except Exception as e:
            logger.error(f"Sort failed: {e}")
            return items
    
    def get_provider_stats(self) -> Dict[str, int]:
        """Get result counts by provider."""
        stats = {}
        for provider in self.providers:
            stats[provider.name] = 0
        return stats
    
    def reset_deduplication(self):
        """Clear deduplication caches."""
        self._seen_urls.clear()
        self._seen_hashes.clear()
