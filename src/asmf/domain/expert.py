"""Domain expertise system for technical validation.

Provides domain-specific validation and analysis capabilities based on
loaded domain configuration. Generic framework applicable to any technical
domain with temperature/pressure/equipment constraints.
"""

import logging
import re
from typing import Dict, List, Optional

from .config import get_domain_config

logger = logging.getLogger(__name__)


class DomainExpert:
    """Domain expertise system for technical validation.

    Provides technical validation based on domain configuration.
    All domain knowledge (temperature ranges, equipment, processes, etc.)
    is loaded from YAML configuration file.
    
    Example usage:
        expert = DomainExpert()
        result = expert.validate_temperature_claim("heating to 500°C")
        if not result["valid"]:
            print(f"Invalid: {result['reason']}")
    """

    # Compile regex patterns at class level for performance
    _TEMP_PATTERN = re.compile(r"(\d+)\s*(?:degrees?\s*)?(?:C|Celsius|°C)")
    _PCT_PATTERN = re.compile(r"(\d+)\s*(?:%|percent)")

    def __init__(self):
        """Initialize with domain configuration."""
        self.config = get_domain_config()
        logger.info("Initialized %s domain expert", self.config.domain_name)

    @property
    def temperature_ranges(self) -> Dict[str, tuple]:
        """Get temperature ranges from config."""
        return self.config.get_temperature_ranges()

    @property
    def equipment_types(self) -> List[str]:
        """Get equipment types from config."""
        return self.config.get_equipment_types()

    @property
    def feedstocks(self) -> List[str]:
        """Get feedstocks from config."""
        return self.config.get_feedstocks()

    @property
    def products(self) -> Dict[str, Dict]:
        """Get products from config."""
        return self.config.get_products()

    @property
    def process_types(self) -> List[str]:
        """Get process types from config."""
        return self.config.get_process_types()

    def validate_temperature_claim(self, text: str) -> Dict:
        """Validate temperature claims for technical feasibility.

        Args:
            text: Technical text to analyze (claim, specification, etc.)

        Returns:
            Dict with 'valid' (bool) and 'reason' (str) keys
        """
        # Extract temperature mentions
        temp_matches = self._TEMP_PATTERN.findall(text)
        temperatures = []
        for match in temp_matches:
            try:
                temperatures.append(int(match))
            except ValueError:
                logger.warning("Failed to parse temperature: %s", match)

        if not temperatures:
            return {"valid": True, "reason": "No specific temperatures claimed"}

        # Check against config
        for temp in temperatures:
            if not self.config.validate_temperature(temp):
                ranges = self.temperature_ranges
                if ranges:
                    all_mins = [r[0] for r in ranges.values()]
                    all_maxs = [r[1] for r in ranges.values()]
                    return {
                        "valid": False,
                        "reason": (
                            f"Temperature {temp}°C outside typical "
                            f"{self.config.domain_name} range "
                            f"(~{min(all_mins)}-{max(all_maxs)}°C)"
                        ),
                    }
                else:
                    return {
                        "valid": False,
                        "reason": f"Temperature {temp}°C may be unrealistic",
                    }

            # Check if temperature matches claimed process type
            for process_type, (min_temp, max_temp) in self.temperature_ranges.items():
                process_name = process_type.replace("_", " ")
                if process_name in text.lower():
                    if not (min_temp <= temp <= max_temp):
                        return {
                            "valid": False,
                            "reason": (
                                f"{process_name.title()} temperature {temp}°C "
                                f"outside typical range {min_temp}-{max_temp}°C"
                            ),
                        }

        return {"valid": True, "reason": "Temperature claims are reasonable"}

    def validate_equipment_design(self, text: str) -> Dict:
        """Validate equipment design claims.

        Args:
            text: Technical text to analyze

        Returns:
            Dict with 'valid' (bool) and 'reason' (str) keys
        """
        text_lower = text.lower()

        # Check for equipment type consistency
        equipment_mentions = sum(
            1 for e in self.equipment_types if e.replace("_", " ") in text_lower
        )
        if equipment_mentions > 2:
            return {
                "valid": True,
                "reason": "Multiple equipment types may indicate hybrid system",
                "warning": "Verify design is not overly complex",
            }

        return {"valid": True, "reason": "Equipment design appears feasible"}

    def identify_process_type(self, text: str) -> Optional[str]:
        """Classify the process type from text.

        Args:
            text: Technical text to analyze

        Returns:
            Process type or None if cannot determine
        """
        text_lower = text.lower()

        # Direct process mentions
        for process in self.process_types:
            if process.lower() in text_lower:
                return process.replace(" ", "_")

        return None

    def get_typical_products_for_process(self, process_type: str) -> Dict[str, str]:
        """Get typical product information for process type.

        Args:
            process_type: Type of process

        Returns:
            Dict of product: description/yield info
        """
        # Return all products from config
        # Domain experts can customize config with process-specific yields
        return {name: info.get("description", "") for name, info in self.products.items()}

    def check_mass_balance(self, text: str) -> Dict:
        """Check if claimed product yields are physically possible.

        Args:
            text: Technical text with yield percentages

        Returns:
            Dict with validation result
        """
        # Extract percentage mentions
        pct_matches = self._PCT_PATTERN.findall(text)
        percentages = []
        for match in pct_matches:
            try:
                percentages.append(int(match))
            except ValueError:
                logger.warning("Failed to parse percentage: %s", match)

        if not percentages:
            return {"valid": True, "reason": "No specific yields claimed"}

        # Check if percentages sum to > 100%
        if sum(percentages) > 105:  # Allow 5% margin for measurement error
            return {
                "valid": False,
                "reason": f"Claimed yields sum to {sum(percentages)}%, exceeding 100%",
            }

        return {"valid": True, "reason": "Yield claims appear balanced"}
