"""
State tracker for managing item status and persistence.

Provides tracking, deduplication, and status management for any
search-match-evaluate workflow.
"""
import json
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Tracker:
    """
    Track items through workflow stages.

    Features:
    - Status management (new, in-progress, completed, rejected)
    - JSON persistence
    - Deduplication
    - History tracking
    - Export capabilities
    """

    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_REJECTED = "rejected"

    VALID_STATUSES = [STATUS_NEW, STATUS_IN_PROGRESS,
                      STATUS_COMPLETED, STATUS_REJECTED]

    def __init__(self, storage_path: str = "data/tracked_items.json"):
        """
        Initialize tracker.

        Args:
            storage_path: Path to JSON storage file
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.items = self._load()

    def _load(self) -> List[Dict]:
        """Load items from storage."""
        if not self.storage_path.exists():
            return []

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load tracked items: %s", e)
            return []

    def _save(self):
        """Save items to storage."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Failed to save tracked items: %s", e)

    def track(self, item: Dict, status: str = STATUS_NEW) -> Optional[str]:
        """
        Add item to tracker.

        Args:
            item: Item dictionary with at minimum 'title' and 'link'
            status: Initial status

        Returns:
            Item ID if tracked, None if duplicate
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        # Check for duplicate
        item_id = self._generate_id(item)
        if self.get_by_id(item_id):
            logger.debug("Duplicate item: %s", item.get("title"))
            return None

        # Add timestamp and metadata
        tracked_item = {
            **item,
            "id": item_id,
            "status": status,
            "tracked_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "history": [{
                "timestamp": datetime.now().isoformat(),
                "action": "tracked",
                "status": status
            }]
        }

        self.items.append(tracked_item)
        self._save()

        logger.info("Tracked item: %s", item_id)
        return item_id

    def update_status(self, item_id: str, new_status: str, note: Optional[str] = None):
        """
        Update item status.

        Args:
            item_id: Item identifier
            new_status: New status value
            note: Optional note for history
        """
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")

        item = self.get_by_id(item_id)
        if not item:
            raise ValueError(f"Item not found: {item_id}")

        old_status = item["status"]
        item["status"] = new_status
        item["updated_at"] = datetime.now().isoformat()

        # Add to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "status_change",
            "old_status": old_status,
            "new_status": new_status
        }

        if note:
            history_entry["note"] = note

        item["history"].append(history_entry)

        self._save()
        logger.info("Updated %s: %s -> %s", item_id, old_status, new_status)

    def get_by_id(self, item_id: str) -> Optional[Dict]:
        """Get item by ID."""
        for item in self.items:
            if item.get("id") == item_id:
                return item
        return None

    def get_all(self, status: Optional[str] = None) -> List[Dict]:
        """
        Get all items, optionally filtered by status.

        Args:
            status: Filter by status (optional)

        Returns:
            List of items
        """
        if status:
            if status not in self.VALID_STATUSES:
                raise ValueError(f"Invalid status: {status}")
            return [item for item in self.items if item.get("status") == status]

        return self.items.copy()

    def delete(self, item_id: str):
        """Delete item by ID."""
        self.items = [item for item in self.items if item.get("id") != item_id]
        self._save()
        logger.info("Deleted item: %s", item_id)

    def clear_all(self):
        """Clear all tracked items."""
        self.items = []
        self._save()
        logger.info("Cleared all tracked items")

    def get_stats(self) -> Dict[str, int]:
        """Get status statistics."""
        stats = {status: 0 for status in self.VALID_STATUSES}

        for item in self.items:
            status = item.get("status", self.STATUS_NEW)
            stats[status] = stats.get(status, 0) + 1

        return stats

    def export_csv(self, output_path: str, status: Optional[str] = None):
        """
        Export items to CSV.

        Args:
            output_path: Output file path
            status: Filter by status (optional)
        """
        import csv

        items = self.get_all(status)
        if not items:
            logger.warning("No items to export")
            return

        # Get all unique keys
        keys = set()
        for item in items:
            keys.update(item.keys())

        keys = sorted(keys - {"history"})  # Exclude history from CSV

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()

            for item in items:
                row = {k: item.get(k, "") for k in keys}
                writer.writerow(row)

        logger.info("Exported %d items to %s", len(items), output_path)

    def _generate_id(self, item: Dict) -> str:
        """Generate unique ID from item content."""
        # Use link as primary identifier
        link = item.get("link", "")
        if link:
            return hashlib.md5(link.encode()).hexdigest()[:16]

        # Fallback to title + description
        content = f"{item.get('title', '')}|{item.get('description', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


# Singleton instance
_tracker_instance = None


def get_tracker(storage_path: Optional[str] = None) -> Tracker:
    """
    Get singleton tracker instance.

    Args:
        storage_path: Optional custom storage path

    Returns:
        Tracker instance
    """
    global _tracker_instance

    if _tracker_instance is None or storage_path:
        _tracker_instance = Tracker(storage_path or "data/tracked_items.json")

    return _tracker_instance
