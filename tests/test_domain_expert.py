"""Tests for domain expert validation system."""

import tempfile
from pathlib import Path

import pytest
import yaml

from asmf.domain import DomainConfig, DomainExpert


@pytest.fixture
def thermal_config():
    """Create thermal processing config for testing."""
    config_data = {
        "domain": {
            "name": "thermal_processing",
            "description": "Thermal systems",
        },
        "temperature_ranges": {
            "pyrolysis": [300, 600],
            "gasification": [600, 900],
        },
        "equipment_types": ["fixed_bed", "fluidized_bed"],
        "feedstocks": ["biomass", "plastic"],
        "products": {
            "bio_oil": {"description": "Liquid fuel", "typical_yield": "50%"},
            "syngas": {"description": "Gas fuel", "typical_yield": "30%"},
            "biochar": {"description": "Solid carbon", "typical_yield": "20%"},
        },
        "process_types": ["pyrolysis", "gasification"],
        "operating_conditions": {
            "pressure": {"min": 1.0, "max": 10.0},
        },
    }
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    # Override global config for testing
    from asmf.domain.config import _domain_config
    original = _domain_config
    
    yield DomainConfig(config_path)
    
    # Cleanup
    config_path.unlink()


@pytest.fixture
def expert(thermal_config, monkeypatch):
    """Create domain expert with test config."""
    from asmf.domain import config as config_module
    
    monkeypatch.setattr(config_module, "_domain_config", thermal_config)
    return DomainExpert()


class TestDomainExpertProperties:
    """Test domain expert property accessors."""
    
    def test_temperature_ranges(self, expert):
        """Test temperature range access."""
        ranges = expert.temperature_ranges
        assert "pyrolysis" in ranges
        assert ranges["pyrolysis"] == (300.0, 600.0)
    
    def test_equipment_types(self, expert):
        """Test equipment type access."""
        equipment = expert.equipment_types
        assert "fixed_bed" in equipment
        assert "fluidized_bed" in equipment
    
    def test_feedstocks(self, expert):
        """Test feedstock access."""
        feedstocks = expert.feedstocks
        assert "biomass" in feedstocks
        assert "plastic" in feedstocks
    
    def test_products(self, expert):
        """Test product access."""
        products = expert.products
        assert "bio_oil" in products
        assert products["bio_oil"]["typical_yield"] == "50%"
    
    def test_process_types(self, expert):
        """Test process type access."""
        processes = expert.process_types
        assert "pyrolysis" in processes
        assert "gasification" in processes


class TestExtractTemperatures:
    """Test temperature extraction helper."""
    
    def test_extract_single_temperature(self, expert):
        """Test extracting single temperature."""
        temps = expert._extract_temperatures("heating to 500°C")
        assert temps == [500]
    
    def test_extract_multiple_temperatures(self, expert):
        """Test extracting multiple temperatures."""
        temps = expert._extract_temperatures("from 300°C to 600 degrees Celsius")
        assert temps == [300, 600]
    
    def test_extract_no_temperatures(self, expert):
        """Test text with no temperatures."""
        temps = expert._extract_temperatures("process at ambient conditions")
        assert temps == []
    
    def test_extract_various_formats(self, expert):
        """Test different temperature formats."""
        temps = expert._extract_temperatures("400°C, 500 degrees C, 600 Celsius")
        assert temps == [400, 500, 600]


class TestCheckTemperatureInRange:
    """Test temperature range validation helper."""
    
    def test_temperature_in_range(self, expert):
        """Test valid temperature."""
        error = expert._check_temperature_in_range(450)
        assert error is None
    
    def test_temperature_outside_range(self, expert):
        """Test temperature outside range."""
        error = expert._check_temperature_in_range(2000)
        assert error is not None
        assert "2000°C" in error
        assert "outside typical" in error
    
    def test_temperature_in_buffer_zone(self, expert):
        """Test temperature in buffer zone."""
        # 100°C below minimum (300-100=200) should be allowed
        error = expert._check_temperature_in_range(200)
        assert error is None


class TestCheckTemperatureProcessMatch:
    """Test process-specific temperature validation."""
    
    def test_temperature_matches_process(self, expert):
        """Test temperature valid for mentioned process."""
        error = expert._check_temperature_process_match(450, "pyrolysis reactor at 450°C")
        assert error is None
    
    def test_temperature_wrong_for_process(self, expert):
        """Test temperature invalid for mentioned process."""
        error = expert._check_temperature_process_match(800, "pyrolysis reactor at 800°C")
        assert error is not None
        assert "Pyrolysis" in error
        assert "800°C" in error
        assert "300" in error and "600" in error  # Check range values
    
    def test_no_process_mentioned(self, expert):
        """Test when no specific process mentioned."""
        error = expert._check_temperature_process_match(450, "heating to 450°C")
        assert error is None


class TestValidateTemperatureClaim:
    """Test main temperature validation method."""
    
    def test_no_temperatures(self, expert):
        """Test text with no temperatures."""
        result = expert.validate_temperature_claim("process uses ambient conditions")
        assert result["valid"] is True
        assert "No specific temperatures" in result["reason"]
    
    def test_valid_temperature(self, expert):
        """Test valid temperature claim."""
        result = expert.validate_temperature_claim("heating to 450°C")
        assert result["valid"] is True
        assert "reasonable" in result["reason"]
    
    def test_invalid_temperature_out_of_range(self, expert):
        """Test temperature outside domain range."""
        result = expert.validate_temperature_claim("heating to 5000°C")
        assert result["valid"] is False
        assert "5000°C" in result["reason"]
    
    def test_temperature_wrong_for_process(self, expert):
        """Test temperature invalid for specific process."""
        result = expert.validate_temperature_claim("pyrolysis at 850°C")
        assert result["valid"] is False
        assert "Pyrolysis" in result["reason"]
        assert "850°C" in result["reason"]
    
    def test_multiple_temperatures_all_valid(self, expert):
        """Test multiple valid temperatures."""
        result = expert.validate_temperature_claim("from 400°C to 500°C")
        assert result["valid"] is True
    
    def test_multiple_temperatures_one_invalid(self, expert):
        """Test fails on first invalid temperature."""
        result = expert.validate_temperature_claim("from 400°C to 5000°C")
        assert result["valid"] is False
        assert "5000°C" in result["reason"]


class TestValidateEquipmentDesign:
    """Test equipment design validation."""
    
    def test_single_equipment_type(self, expert):
        """Test single equipment mention."""
        result = expert.validate_equipment_design("using a fixed bed reactor")
        assert result["valid"] is True
    
    def test_multiple_equipment_types(self, expert):
        """Test multiple equipment types (potential warning)."""
        result = expert.validate_equipment_design(
            "comparing fixed bed, fluidized bed, and rotary kiln reactors"
        )
        assert result["valid"] is True
        if "warning" in result:
            assert "not overly complex" in result["warning"]


class TestIdentifyProcessType:
    """Test process type identification."""
    
    def test_identify_pyrolysis(self, expert):
        """Test identifying pyrolysis process."""
        process = expert.identify_process_type("thermal pyrolysis of biomass")
        assert process == "pyrolysis"
    
    def test_identify_gasification(self, expert):
        """Test identifying gasification process."""
        process = expert.identify_process_type("biomass gasification process")
        assert process == "gasification"
    
    def test_no_process_identified(self, expert):
        """Test when no process can be identified."""
        process = expert.identify_process_type("heating and cooling cycle")
        assert process is None


class TestGetTypicalProducts:
    """Test product information retrieval."""
    
    def test_get_typical_products(self, expert):
        """Test getting product descriptions."""
        products = expert.get_typical_products_for_process("pyrolysis")
        
        assert "bio_oil" in products
        assert "Liquid fuel" in products["bio_oil"]
        assert "syngas" in products
        assert "biochar" in products


class TestCheckMassBalance:
    """Test mass balance validation."""
    
    def test_no_yields_claimed(self, expert):
        """Test when no yields mentioned."""
        result = expert.check_mass_balance("produces bio-oil and syngas")
        assert result["valid"] is True
        assert "No specific yields" in result["reason"]
    
    def test_valid_mass_balance(self, expert):
        """Test valid yield percentages."""
        result = expert.check_mass_balance("50% bio-oil, 30% syngas, 20% biochar")
        assert result["valid"] is True
        assert "balanced" in result["reason"]
    
    def test_yields_sum_to_100_with_margin(self, expert):
        """Test yields at 105% (within margin)."""
        result = expert.check_mass_balance("55% bio-oil, 35% syngas, 15% biochar")
        assert result["valid"] is True
    
    def test_yields_exceed_100(self, expert):
        """Test yields exceeding 100%."""
        result = expert.check_mass_balance("60% bio-oil, 50% syngas, 40% biochar")
        assert result["valid"] is False
        assert "150%" in result["reason"]
        assert "exceeding 100%" in result["reason"]
    
    def test_single_high_yield(self, expert):
        """Test single yield over 100%."""
        result = expert.check_mass_balance("yields 120% bio-oil")
        assert result["valid"] is False
