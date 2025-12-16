"""Domain-specific configuration and validation system.

This package provides a flexible framework for defining and validating
domain-specific technical knowledge through YAML configuration files.

Key components:
- DomainConfig: Load and manage domain configuration from YAML
- DomainExpert: Validate technical parameters against domain rules

Supports any technical domain with configurable:
- Temperature/pressure ranges
- Equipment/reactor types
- Process types and materials
- Operating conditions
- Validation rules
"""

from .config import DomainConfig, get_domain_config
from .expert import DomainExpert

__all__ = ["DomainConfig", "get_domain_config", "DomainExpert"]
