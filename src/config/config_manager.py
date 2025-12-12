"""Configuration manager for loading and updating settings."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manage application configuration.
    
    Handles:
    - Loading config from JSON
    - Runtime updates
    - Environment variable overrides
    - Default values
    """
    
    DEFAULT_CONFIG = {
        "system_instructions": "Evaluate items for relevance and quality.",
        "blocked_entities": [],
        "providers": {},
        "evaluation": {
            "score_threshold": 0.7,
            "batch_size": 10,
            "criteria": "Evaluate items for quality and relevance"
        },
        "deduplication": {
            "enabled": True,
            "method": "url"
        },
        "tracking": {
            "storage_path": "data/tracked_items.json"
        },
        "llm": {
            "default_provider": "openai",
            "fallback_chain": ["openai", "anthropic", "gemini", "ollama"],
            "max_tokens": 2000,
            "temperature": 0.7
        },
        "rate_limiting": {
            "enabled": True,
            "calls_per_second": 2
        },
        "logging": {
            "level": "INFO",
            "file": "logs/framework.log"
        }
    }
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config JSON file
        """
        self.config_path = Path(config_path)
        self.config = self._load()
    
    def _load(self) -> Dict:
        """Load configuration from file."""
        if not self.config_path.exists():
            logger.warning("Config file not found, using defaults: %s", self.config_path)
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            
            # Merge with defaults
            config = self.DEFAULT_CONFIG.copy()
            self._deep_merge(config, user_config)
            
            logger.info("Loaded config from: %s", self.config_path)
            return config
            
        except Exception as e:
            logger.error("Failed to load config: %s", e)
            return self.DEFAULT_CONFIG.copy()
    
    def _deep_merge(self, base: Dict, update: Dict):
        """Recursively merge update into base."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get config value by dot-notation key.
        
        Args:
            key: Config key (e.g., "evaluation.score_threshold")
            default: Default value if key not found
            
        Returns:
            Config value or default
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set config value by dot-notation key.
        
        Args:
            key: Config key (e.g., "evaluation.score_threshold")
            value: New value
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info("Saved config to: %s", self.config_path)
            
        except Exception as e:
            logger.error("Failed to save config: %s", e)
    
    def add_blocked_entity(self, entity_type: str, value: str, reason: str = ""):
        """
        Add entity to block list.
        
        Args:
            entity_type: Type of entity (site, employer, keyword)
            value: Entity value to block
            reason: Optional reason for blocking
        """
        blocked = self.get("blocked_entities", [])
        
        # Check if already exists
        for item in blocked:
            if item.get("type") == entity_type and item.get("value") == value:
                logger.debug("Entity already blocked: %s=%s", entity_type, value)
                return
        
        blocked.append({
            "type": entity_type,
            "value": value,
            "reason": reason
        })
        
        self.set("blocked_entities", blocked)
        logger.info("Added blocked entity: %s=%s", entity_type, value)
    
    def remove_blocked_entity(self, entity_type: str, value: str):
        """
        Remove entity from block list.
        
        Args:
            entity_type: Type of entity (site, employer, keyword)
            value: Entity value to unblock
        """
        blocked = self.get("blocked_entities", [])
        
        updated = [
            item for item in blocked
            if not (item.get("type") == entity_type and item.get("value") == value)
        ]
        
        if len(updated) < len(blocked):
            self.set("blocked_entities", updated)
            logger.info("Removed blocked entity: %s=%s", entity_type, value)
        else:
            logger.debug("Entity not found: %s=%s", entity_type, value)
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict]:
        """Get configuration for specific provider."""
        providers = self.get("providers", {})
        return providers.get(provider_name)
    
    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if provider is enabled."""
        provider_config = self.get_provider_config(provider_name)
        if not provider_config:
            return False
        return provider_config.get("enabled", False)


# Singleton instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get singleton config instance.
    
    Args:
        config_path: Optional custom config path
        
    Returns:
        ConfigManager instance
    """
    global _config_instance
    
    if _config_instance is None or config_path:
        _config_instance = ConfigManager(config_path or "config.json")
    
    return _config_instance
