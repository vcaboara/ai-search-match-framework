"""Domain configuration management for technical analysis.

Provides YAML-based configuration for domain-specific technical knowledge
and validation rules. Supports any technical domain with configurable:
- Temperature/pressure ranges
- Equipment/reactor types  
- Process types and materials
- Operating conditions
- Validation thresholds
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)


class DomainConfig:
    """Load and manage domain-specific expertise configuration.

    Example YAML structure:
        domain:
          name: "thermal_processing"
          description: "Thermal decomposition and energy conversion"

        temperature_ranges:
          low_temp: [200, 400]
          high_temp: [600, 900]

        equipment_types:
          - fixed_bed_reactor
          - fluidized_bed

        process_types:
          - pyrolysis
          - gasification
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize domain configuration.

        Args:
            config_path: Path to domain config YAML file. Defaults to config/domain.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / \
                "config" / "domain.yaml"

        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(
                "Domain config not found at %s, using default config", self.config_path)
            self.config = self._get_default_config()
            return

        try:
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f) or {}
            logger.info("Loaded domain config from %s", self.config_path)
        except Exception as e:
            logger.error("Failed to load domain config: %s", e)
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return minimal default configuration."""
        return {
            "domain": {"name": "general", "description": "General technical analysis"},
            "temperature_ranges": {},
            "equipment_types": [],
            "feedstocks": [],
            "products": {},
            "process_types": [],
            "operating_conditions": {},
        }

    @property
    def domain_name(self) -> str:
        """Get domain name."""
        return self.config.get("domain", {}).get("name", "general")

    @property
    def domain_description(self) -> str:
        """Get domain description."""
        return self.config.get("domain", {}).get("description", "")

    def get_temperature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Get temperature ranges for different process types.

        Returns:
            Dict mapping process type to (min_temp, max_temp) tuple in Celsius
        """
        if not hasattr(self, '_temperature_ranges_cache'):
            self._temperature_ranges_cache = self._compute_temperature_ranges()
        return self._temperature_ranges_cache

    def _compute_temperature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Compute temperature ranges from config."""
        ranges = self.config.get("temperature_ranges", {})
        valid_ranges = {}
        for k, v in ranges.items():
            if (
                isinstance(v, (list, tuple))
                and len(v) == 2
                and all(isinstance(x, (int, float)) for x in v)
            ):
                valid_ranges[k] = (float(v[0]), float(v[1]))
            else:
                logger.warning(
                    "Invalid temperature range for key '%s': %r. "
                    "Expected a list or tuple of two numbers.",
                    k,
                    v,
                )
        return valid_ranges

    def get_equipment_types(self) -> List[str]:
        """Get valid equipment/reactor types."""
        if not hasattr(self, '_equipment_types_cache'):
            self._equipment_types_cache = self.config.get(
                "equipment_types", [])
        return self._equipment_types_cache

    def get_feedstocks(self) -> List[str]:
        """Get known feedstock/input materials."""
        if not hasattr(self, '_feedstocks_cache'):
            self._feedstocks_cache = self.config.get("feedstocks", [])
        return self._feedstocks_cache

    def get_products(self) -> Dict[str, Dict[str, str]]:
        """Get product information with metadata.

        Returns:
            Dict mapping product name to metadata dict (description, yield, etc.)
        """
        if not hasattr(self, '_products_cache'):
            self._products_cache = self.config.get("products", {})
        return self._products_cache

    def get_product_names(self) -> List[str]:
        """Get list of product names."""
        if not hasattr(self, '_product_names_cache'):
            self._product_names_cache = list(self.get_products().keys())
        return self._product_names_cache

    def get_process_types(self) -> List[str]:
        """Get known process types."""
        if not hasattr(self, '_process_types_cache'):
            self._process_types_cache = self.config.get("process_types", [])
        return self._process_types_cache

    def get_operating_conditions(self) -> Dict[str, Any]:
        """Get operating condition ranges (pressure, residence time, etc.)."""
        if not hasattr(self, '_operating_conditions_cache'):
            self._operating_conditions_cache = self.config.get(
                "operating_conditions", {})
        return self._operating_conditions_cache

    def validate_temperature(self, temp_celsius: float) -> bool:
        """Check if temperature is within reasonable range for this domain.

        Args:
            temp_celsius: Temperature in Celsius

        Returns:
            True if temperature is valid
        """
        ranges = self.get_temperature_ranges()
        if not ranges:
            # No ranges defined, accept reasonable general range
            return -50 <= temp_celsius <= 2000

        # Check if temp falls in any defined range
        for range_min, range_max in ranges.values():
            if range_min <= temp_celsius <= range_max:
                return True

        # Also allow temps slightly outside ranges (buffer zone for edge cases)
        all_mins = [r[0] for r in ranges.values()]
        all_maxs = [r[1] for r in ranges.values()]
        if all_mins and all_maxs:
            return (min(all_mins) - 100) <= temp_celsius <= (max(all_maxs) + 200)

        return False

    def validate_pressure(self, pressure_bar: float) -> bool:
        """Check if pressure is within reasonable range.

        Args:
            pressure_bar: Pressure in bar

        Returns:
            True if pressure is valid
        """
        conditions = self.get_operating_conditions()
        pressure_range = conditions.get("pressure", {})

        min_pressure = pressure_range.get("min", 0.1)
        max_pressure = pressure_range.get("max", 1000)

        return min_pressure <= pressure_bar <= max_pressure


# Global instance - loaded once
_domain_config: Optional[DomainConfig] = None


def get_domain_config(config_path: Optional[Path] = None) -> DomainConfig:
    """Get global domain configuration instance.

    Args:
        config_path: Optional path to config file (only used on first call)

    Returns:
        DomainConfig instance
    """
    global _domain_config
    if _domain_config is None or config_path is not None:
        _domain_config = DomainConfig(config_path)
    return _domain_config
