"""Tests for task-specific model selection."""

import pytest
from unittest.mock import patch, MagicMock
from asmf.llm import ModelSelector, TaskType


class TestModelSelector:
    """Test ModelSelector functionality."""
    
    def test_init_with_manual_vram(self):
        """Test initialization with manual VRAM override."""
        selector = ModelSelector(vram_gb=16.0)
        assert selector.vram_gb == 16.0
        assert selector.has_gpu is True
        assert selector.gpu_vendor == "Manual Override"
    
    def test_init_with_zero_vram(self):
        """Test initialization with no GPU."""
        selector = ModelSelector(vram_gb=0)
        assert selector.vram_gb == 0
        assert selector.has_gpu is False
    
    @patch('subprocess.run')
    def test_detect_nvidia_gpu(self, mock_run):
        """Test NVIDIA GPU detection."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="8192, NVIDIA GeForce RTX 3070\n"
        )
        
        selector = ModelSelector()
        assert selector.has_gpu is True
        assert selector.gpu_vendor == "NVIDIA"
        assert selector.vram_gb == 8.0
    
    @patch('subprocess.run')
    def test_detect_amd_gpu(self, mock_run):
        """Test AMD GPU detection."""
        # First call (nvidia-smi) fails, second (rocm-smi) succeeds
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""),
            MagicMock(returncode=0, stdout="GPU 0: VRAM info...")
        ]
        
        selector = ModelSelector()
        assert selector.has_gpu is True
        assert selector.gpu_vendor == "AMD"
        assert selector.vram_gb == 8  # Default estimate
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_detect_apple_silicon(self, mock_run, mock_system):
        """Test Apple Silicon detection."""
        mock_system.return_value = "Darwin"
        
        # nvidia-smi fails, rocm-smi fails, sysctl succeeds
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""),  # nvidia-smi
            MagicMock(returncode=1, stdout=""),  # rocm-smi
            MagicMock(returncode=0, stdout="Apple M2 Pro"),  # cpu brand
            MagicMock(returncode=0, stdout="34359738368")  # 32GB RAM
        ]
        
        selector = ModelSelector()
        assert selector.has_gpu is True
        assert selector.gpu_vendor == "Apple"
        assert selector.vram_gb == 19.2  # 60% of 32GB
    
    @patch('subprocess.run')
    def test_no_gpu_detected(self, mock_run):
        """Test when no GPU is detected."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        
        selector = ModelSelector()
        assert selector.has_gpu is False
        assert selector.gpu_vendor is None
        assert selector.vram_gb == 0
    
    def test_vram_tier_high(self):
        """Test high VRAM tier classification."""
        selector = ModelSelector(vram_gb=16.0)
        assert selector._get_vram_tier() == "high"
    
    def test_vram_tier_mid(self):
        """Test mid VRAM tier classification."""
        selector = ModelSelector(vram_gb=8.0)
        assert selector._get_vram_tier() == "mid"
    
    def test_vram_tier_low(self):
        """Test low VRAM tier classification."""
        selector = ModelSelector(vram_gb=4.0)
        assert selector._get_vram_tier() == "low"
    
    def test_get_recommendations_code_review_high_vram(self):
        """Test code review recommendations for high-end GPU."""
        selector = ModelSelector(vram_gb=16.0)
        recs = selector.get_recommendations(TaskType.CODE_REVIEW)
        
        assert len(recs) > 0
        assert recs[0].name == "qwen2.5-coder:32b"
        assert recs[0].task_optimized is True
    
    def test_get_recommendations_code_generation_mid_vram(self):
        """Test code generation recommendations for mid-range GPU."""
        selector = ModelSelector(vram_gb=8.0)
        recs = selector.get_recommendations(TaskType.CODE_GENERATION)
        
        assert len(recs) > 0
        assert "coder" in recs[0].name  # Should prioritize coder models
        assert recs[0].task_optimized is True
    
    def test_get_recommendations_document_analysis_low_vram(self):
        """Test document analysis recommendations for low-end GPU."""
        selector = ModelSelector(vram_gb=4.0)
        recs = selector.get_recommendations(TaskType.DOCUMENT_ANALYSIS)
        
        assert len(recs) > 0
        assert recs[0].size_gb <= 4.0  # Should fit in VRAM
    
    def test_get_recommendations_general(self):
        """Test general task recommendations."""
        selector = ModelSelector(vram_gb=12.0)
        recs = selector.get_recommendations(TaskType.GENERAL)
        
        assert len(recs) > 0
        assert recs[0].quality in ["Excellent", "Very Good", "Good"]
    
    def test_select_model_without_availability_check(self):
        """Test model selection without checking Ollama."""
        selector = ModelSelector(vram_gb=16.0)
        model = selector.select_model(
            TaskType.CODE_REVIEW,
            check_availability=False
        )
        
        assert model == "qwen2.5-coder:32b"
    
    @patch('httpx.get')
    def test_select_model_with_availability_check(self, mock_get):
        """Test model selection with Ollama availability check."""
        # Mock Ollama API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "qwen2.5-coder:14b"},
                {"name": "llama3.2:3b"}
            ]
        }
        mock_get.return_value = mock_response
        
        selector = ModelSelector(vram_gb=16.0)
        model = selector.select_model(
            TaskType.CODE_REVIEW,
            check_availability=True
        )
        
        # Should select first available from recommendations
        assert model == "qwen2.5-coder:14b"
    
    @patch('httpx.get')
    def test_select_model_none_available(self, mock_get):
        """Test model selection when no recommended models available."""
        # Mock empty Ollama
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        selector = ModelSelector(vram_gb=16.0)
        model = selector.select_model(
            TaskType.CODE_REVIEW,
            check_availability=True
        )
        
        # Should return top recommendation even if not available
        assert model == "qwen2.5-coder:32b"
    
    @patch('httpx.get')
    def test_list_available_models(self, mock_get):
        """Test listing available models from Ollama."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:3b"},
                {"name": "qwen2.5:14b-q4"}
            ]
        }
        mock_get.return_value = mock_response
        
        selector = ModelSelector(vram_gb=8.0)
        models = selector._list_available_models()
        
        assert "llama3.2:3b" in models
        assert "qwen2.5:14b-q4" in models
        assert len(models) == 2
    
    @patch('httpx.get')
    def test_list_available_models_connection_error(self, mock_get):
        """Test graceful handling of Ollama connection errors."""
        mock_get.side_effect = Exception("Connection refused")
        
        selector = ModelSelector(vram_gb=8.0)
        models = selector._list_available_models()
        
        # Should return empty list on error
        assert models == []
    
    def test_all_task_types_have_recommendations(self):
        """Test that all task types have recommendations for all tiers."""
        selector_high = ModelSelector(vram_gb=16.0)
        selector_mid = ModelSelector(vram_gb=8.0)
        selector_low = ModelSelector(vram_gb=4.0)
        
        for task_type in TaskType:
            # All selectors should have recommendations
            recs_high = selector_high.get_recommendations(task_type)
            recs_mid = selector_mid.get_recommendations(task_type)
            recs_low = selector_low.get_recommendations(task_type)
            
            assert len(recs_high) > 0, f"No high-tier recs for {task_type}"
            assert len(recs_mid) > 0, f"No mid-tier recs for {task_type}"
            assert len(recs_low) > 0, f"No low-tier recs for {task_type}"
    
    def test_task_optimized_models_for_code_tasks(self):
        """Test that code tasks get task-optimized models."""
        selector = ModelSelector(vram_gb=16.0)
        
        code_review_recs = selector.get_recommendations(TaskType.CODE_REVIEW)
        code_gen_recs = selector.get_recommendations(TaskType.CODE_GENERATION)
        
        # Top recommendation should be task-optimized for code
        assert code_review_recs[0].task_optimized is True
        assert code_gen_recs[0].task_optimized is True
        assert "coder" in code_review_recs[0].name.lower()
        assert "coder" in code_gen_recs[0].name.lower()
    
    def test_print_recommendations(self, capsys):
        """Test printing recommendations to console."""
        selector = ModelSelector(vram_gb=8.0)
        selector.print_recommendations(TaskType.CODE_REVIEW)
        
        captured = capsys.readouterr()
        assert "Code Review" in captured.out
        assert "8.0GB VRAM" in captured.out
        assert "qwen2.5-coder" in captured.out
    
    def test_model_size_fits_vram(self):
        """Test that recommended models fit within VRAM constraints."""
        selector_low = ModelSelector(vram_gb=4.0)
        selector_mid = ModelSelector(vram_gb=8.0)
        selector_high = ModelSelector(vram_gb=16.0)
        
        for task_type in TaskType:
            # Low VRAM: top model should fit in 4-6GB
            low_rec = selector_low.get_recommendations(task_type)[0]
            assert low_rec.size_gb <= 6.0
            
            # Mid VRAM: top model should fit in 8-10GB
            mid_rec = selector_mid.get_recommendations(task_type)[0]
            assert mid_rec.size_gb <= 10.0
            
            # High VRAM: can use larger models
            high_rec = selector_high.get_recommendations(task_type)[0]
            # No upper limit, but should be reasonable
            assert high_rec.size_gb > 0


class TestTaskType:
    """Test TaskType enum."""
    
    def test_task_type_values(self):
        """Test that all task types have expected values."""
        assert TaskType.CODE_REVIEW.value == "code_review"
        assert TaskType.CODE_GENERATION.value == "code_generation"
        assert TaskType.DOCUMENT_ANALYSIS.value == "document_analysis"
        assert TaskType.GENERAL.value == "general"
    
    def test_task_type_members(self):
        """Test that all expected task types exist."""
        task_names = [t.name for t in TaskType]
        assert "CODE_REVIEW" in task_names
        assert "CODE_GENERATION" in task_names
        assert "DOCUMENT_ANALYSIS" in task_names
        assert "GENERAL" in task_names
