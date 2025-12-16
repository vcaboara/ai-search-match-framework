"""Tests for domain configuration system."""

import tempfile
from pathlib import Path

import pytest
import yaml

from asmf.domain import DomainConfig, get_domain_config


@pytest.fixture
def sample_config():
    """Sample domain configuration."""
    return {
        "domain": {
            "name": "thermal_processing",
            "description": "Test thermal systems",
        },
        "temperature_ranges": {
            "low_temp": [200, 400],
            "high_temp": [600, 900],
        },
        "equipment_types": ["reactor_a", "reactor_b"],
        "feedstocks": ["biomass", "plastic"],
        "products": {
            "bio_oil": {"description": "Liquid fuel", "typical_yield": "50%"},
            "syngas": {"description": "Gas fuel"},
        },
        "process_types": ["pyrolysis", "gasification"],
        "operating_conditions": {
            "pressure": {"min": 1.0, "max": 10.0},
        },
    }


@pytest.fixture
def config_file(sample_config, tmp_path):
    """Create temporary config file."""
    config_path = tmp_path / "domain.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f)
    return config_path


def test_domain_config_loads_from_file(config_file):
    """Test loading configuration from YAML file."""
    config = DomainConfig(config_file)
    assert config.domain_name == "thermal_processing"
    assert config.domain_description == "Test thermal systems"


def test_domain_config_default_when_file_missing():
    """Test default config when file doesn't exist."""
    config = DomainConfig(Path("/nonexistent/path.yaml"))
    assert config.domain_name == "general"
    assert config.domain_description == "General technical analysis"


def test_get_temperature_ranges(config_file):
    """Test temperature range extraction."""
    config = DomainConfig(config_file)
    ranges = config.get_temperature_ranges()

    assert "low_temp" in ranges
    assert ranges["low_temp"] == (200.0, 400.0)
    assert ranges["high_temp"] == (600.0, 900.0)


def test_get_temperature_ranges_cached(config_file):
    """Test temperature ranges are cached."""
    config = DomainConfig(config_file)
    ranges1 = config.get_temperature_ranges()
    ranges2 = config.get_temperature_ranges()

    # Should return same object (cached)
    assert ranges1 is ranges2


def test_get_temperature_ranges_invalid_format():
    """Test handling of invalid temperature ranges."""
    config_data = {
        "domain": {"name": "test"},
        "temperature_ranges": {
            "valid": [100, 200],
            "invalid_single": [100],
            "invalid_string": "100-200",
            "invalid_mixed": [100, "high"],
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)

    try:
        config = DomainConfig(config_path)
        ranges = config.get_temperature_ranges()

        # Only valid range should be included
        assert "valid" in ranges
        assert "invalid_single" not in ranges
        assert "invalid_string" not in ranges
        assert "invalid_mixed" not in ranges
    finally:
        config_path.unlink()


def test_get_equipment_types(config_file):
    """Test equipment type extraction."""
    config = DomainConfig(config_file)
    equipment = config.get_equipment_types()

    assert len(equipment) == 2
    assert "reactor_a" in equipment
    assert "reactor_b" in equipment


def test_get_feedstocks(config_file):
    """Test feedstock extraction."""
    config = DomainConfig(config_file)
    feedstocks = config.get_feedstocks()

    assert len(feedstocks) == 2
    assert "biomass" in feedstocks
    assert "plastic" in feedstocks


def test_get_products(config_file):
    """Test product extraction."""
    config = DomainConfig(config_file)
    products = config.get_products()

    assert "bio_oil" in products
    assert products["bio_oil"]["description"] == "Liquid fuel"
    assert products["bio_oil"]["typical_yield"] == "50%"
    assert "syngas" in products


def test_get_product_names(config_file):
    """Test product name list."""
    config = DomainConfig(config_file)
    names = config.get_product_names()

    assert len(names) == 2
    assert "bio_oil" in names
    assert "syngas" in names


def test_get_process_types(config_file):
    """Test process type extraction."""
    config = DomainConfig(config_file)
    processes = config.get_process_types()

    assert len(processes) == 2
    assert "pyrolysis" in processes
    assert "gasification" in processes


def test_get_operating_conditions(config_file):
    """Test operating condition extraction."""
    config = DomainConfig(config_file)
    conditions = config.get_operating_conditions()

    assert "pressure" in conditions
    assert conditions["pressure"]["min"] == 1.0
    assert conditions["pressure"]["max"] == 10.0


def test_validate_temperature_in_range(config_file):
    """Test temperature validation."""
    config = DomainConfig(config_file)

    # Within low_temp range
    assert config.validate_temperature(300) is True

    # Within high_temp range
    assert config.validate_temperature(750) is True

    # In buffer zone (100°C below min)
    assert config.validate_temperature(100) is True

    # In buffer zone (200°C above max)
    assert config.validate_temperature(1100) is True

    # Way outside ranges
    assert config.validate_temperature(-200) is False
    assert config.validate_temperature(5000) is False


def test_validate_temperature_no_ranges():
    """Test temperature validation with no configured ranges."""
    config = DomainConfig(Path("/nonexistent.yaml"))

    # Should accept reasonable general range
    assert config.validate_temperature(25) is True
    assert config.validate_temperature(500) is True
    assert config.validate_temperature(1500) is True

    # Should reject extreme values
    assert config.validate_temperature(-100) is False
    assert config.validate_temperature(3000) is False


def test_validate_pressure(config_file):
    """Test pressure validation."""
    config = DomainConfig(config_file)

    # Within range
    assert config.validate_pressure(5.0) is True

    # At boundaries
    assert config.validate_pressure(1.0) is True
    assert config.validate_pressure(10.0) is True

    # Outside range
    assert config.validate_pressure(0.5) is False
    assert config.validate_pressure(15.0) is False


def test_validate_pressure_default_range():
    """Test pressure validation with default range."""
    config = DomainConfig(Path("/nonexistent.yaml"))

    # Should use default range (0.1-1000 bar)
    assert config.validate_pressure(1.0) is True
    assert config.validate_pressure(100.0) is True

    assert config.validate_pressure(0.05) is False
    assert config.validate_pressure(1500.0) is False


def test_global_config_singleton():
    """Test global config instance management."""
    # First call creates instance
    config1 = get_domain_config()

    # Second call returns same instance
    config2 = get_domain_config()
    assert config1 is config2


def test_global_config_can_override_path(config_file):
    """Test overriding global config path."""
    # Override with specific path
    config = get_domain_config(config_file)
    assert config.domain_name == "thermal_processing"
