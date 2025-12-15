"""Task-specific model selection with VRAM detection.

This module provides automatic model selection based on:
1. Available GPU VRAM
2. Task type (code review, generation, document analysis, etc.)
3. Model availability in Ollama

Example:
    >>> from asmf.llm import ModelSelector, TaskType
    >>> selector = ModelSelector()
    >>> model = selector.select_model(TaskType.CODE_REVIEW)
    >>> print(f"Selected: {model}")
    Selected: qwen2.5-coder:32b
"""

import logging
import os
import platform
import subprocess
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks for model selection."""
    CODE_REVIEW = "code_review"
    CODE_GENERATION = "code_generation"
    DOCUMENT_ANALYSIS = "document_analysis"
    GENERAL = "general"


@dataclass
class ModelRecommendation:
    """Model recommendation with metadata."""
    name: str
    size_gb: float
    quality: str
    speed: str
    description: str
    task_optimized: bool = False


class ModelSelector:
    """Select optimal Ollama models based on VRAM and task type.
    
    Provides intelligent model selection that considers:
    - Available GPU VRAM (4GB, 8GB, 12GB+)
    - Task requirements (code, documents, general)
    - Model availability in local Ollama instance
    
    Attributes:
        vram_gb: Detected VRAM in gigabytes
        has_gpu: Whether GPU is available
        gpu_vendor: GPU vendor (NVIDIA, AMD, Apple, None)
    """
    
    # Model recommendations by VRAM tier and task type
    # Format: {vram_tier: {task_type: [models_in_priority_order]}}
    RECOMMENDATIONS = {
        "high": {  # 12GB+ VRAM
            TaskType.CODE_REVIEW: [
                ModelRecommendation(
                    name="qwen2.5-coder:32b",
                    size_gb=21.0,
                    quality="Excellent",
                    speed="2-5 tok/s",
                    description="Best for thorough code review with deep analysis",
                    task_optimized=True
                ),
                ModelRecommendation(
                    name="qwen2.5-coder:14b",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Fast alternative for code review",
                    task_optimized=True
                ),
            ],
            TaskType.CODE_GENERATION: [
                ModelRecommendation(
                    name="qwen2.5-coder:32b",
                    size_gb=21.0,
                    quality="Excellent",
                    speed="2-5 tok/s",
                    description="Best code generation with strong reasoning",
                    task_optimized=True
                ),
                ModelRecommendation(
                    name="qwen2.5-coder:14b",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Balanced code generation",
                    task_optimized=True
                ),
            ],
            TaskType.DOCUMENT_ANALYSIS: [
                ModelRecommendation(
                    name="qwen2.5:32b-q4",
                    size_gb=20.0,
                    quality="Excellent",
                    speed="2-5 tok/s",
                    description="Best for complex document understanding",
                    task_optimized=False
                ),
                ModelRecommendation(
                    name="qwen2.5:14b-q4",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Good document analysis with faster inference",
                    task_optimized=False
                ),
            ],
            TaskType.GENERAL: [
                ModelRecommendation(
                    name="qwen2.5:32b-q4",
                    size_gb=20.0,
                    quality="Excellent",
                    speed="2-5 tok/s",
                    description="Best general-purpose model",
                    task_optimized=False
                ),
                ModelRecommendation(
                    name="qwen2.5:14b-q4",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Fast general-purpose alternative",
                    task_optimized=False
                ),
            ],
        },
        "mid": {  # 8GB VRAM
            TaskType.CODE_REVIEW: [
                ModelRecommendation(
                    name="qwen2.5-coder:14b",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Best code review for mid-range GPUs",
                    task_optimized=True
                ),
                ModelRecommendation(
                    name="qwen2.5-coder:7b",
                    size_gb=4.5,
                    quality="Good",
                    speed="10-15 tok/s",
                    description="Faster code review",
                    task_optimized=True
                ),
            ],
            TaskType.CODE_GENERATION: [
                ModelRecommendation(
                    name="qwen2.5-coder:14b",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Good code generation",
                    task_optimized=True
                ),
                ModelRecommendation(
                    name="qwen2.5-coder:7b",
                    size_gb=4.5,
                    quality="Good",
                    speed="10-15 tok/s",
                    description="Faster code generation",
                    task_optimized=True
                ),
            ],
            TaskType.DOCUMENT_ANALYSIS: [
                ModelRecommendation(
                    name="qwen2.5:14b-q4",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Good document understanding",
                    task_optimized=False
                ),
                ModelRecommendation(
                    name="llama3.2:3b",
                    size_gb=2.0,
                    quality="Good",
                    speed="10-20 tok/s",
                    description="Fast basic analysis",
                    task_optimized=False
                ),
            ],
            TaskType.GENERAL: [
                ModelRecommendation(
                    name="qwen2.5:14b-q4",
                    size_gb=9.0,
                    quality="Very Good",
                    speed="5-10 tok/s",
                    description="Best balance for general use",
                    task_optimized=False
                ),
                ModelRecommendation(
                    name="mistral:7b-q4",
                    size_gb=4.0,
                    quality="Good",
                    speed="8-15 tok/s",
                    description="Fast general-purpose",
                    task_optimized=False
                ),
            ],
        },
        "low": {  # <8GB VRAM or CPU
            TaskType.CODE_REVIEW: [
                ModelRecommendation(
                    name="qwen2.5-coder:7b",
                    size_gb=4.5,
                    quality="Good",
                    speed="5-10 tok/s (GPU), 1-2 tok/s (CPU)",
                    description="Best code review for limited hardware",
                    task_optimized=True
                ),
                ModelRecommendation(
                    name="llama3.2:3b",
                    size_gb=2.0,
                    quality="Fair",
                    speed="10-20 tok/s (GPU), 2-5 tok/s (CPU)",
                    description="Basic code review",
                    task_optimized=False
                ),
            ],
            TaskType.CODE_GENERATION: [
                ModelRecommendation(
                    name="qwen2.5-coder:7b",
                    size_gb=4.5,
                    quality="Good",
                    speed="5-10 tok/s (GPU), 1-2 tok/s (CPU)",
                    description="Decent code generation",
                    task_optimized=True
                ),
                ModelRecommendation(
                    name="llama3.2:3b",
                    size_gb=2.0,
                    quality="Fair",
                    speed="10-20 tok/s (GPU), 2-5 tok/s (CPU)",
                    description="Basic code generation",
                    task_optimized=False
                ),
            ],
            TaskType.DOCUMENT_ANALYSIS: [
                ModelRecommendation(
                    name="llama3.2:3b",
                    size_gb=2.0,
                    quality="Good",
                    speed="10-20 tok/s (GPU), 2-5 tok/s (CPU)",
                    description="Best for limited hardware",
                    task_optimized=False
                ),
                ModelRecommendation(
                    name="qwen2.5:7b-q4",
                    size_gb=4.0,
                    quality="Good",
                    speed="5-10 tok/s (GPU), 1-3 tok/s (CPU)",
                    description="Better quality, slower",
                    task_optimized=False
                ),
            ],
            TaskType.GENERAL: [
                ModelRecommendation(
                    name="llama3.2:3b",
                    size_gb=2.0,
                    quality="Good",
                    speed="10-20 tok/s (GPU), 2-5 tok/s (CPU)",
                    description="Best for limited hardware",
                    task_optimized=False
                ),
                ModelRecommendation(
                    name="phi3:mini",
                    size_gb=2.0,
                    quality="Good",
                    speed="10-15 tok/s",
                    description="Efficient Microsoft model",
                    task_optimized=False
                ),
            ],
        },
    }
    
    def __init__(self, vram_gb: Optional[float] = None):
        """Initialize ModelSelector.
        
        Args:
            vram_gb: Override VRAM detection with specific value.
                     If None, auto-detects GPU VRAM.
        """
        if vram_gb is not None:
            self.vram_gb = vram_gb
            self.has_gpu = vram_gb > 0
            self.gpu_vendor = "Manual Override"
        else:
            gpu_info = self._detect_gpu()
            self.vram_gb = gpu_info["vram_gb"]
            self.has_gpu = gpu_info["has_gpu"]
            self.gpu_vendor = gpu_info["vendor"]
        
        logger.info(
            f"ModelSelector initialized: {self.vram_gb}GB VRAM, "
            f"GPU: {self.has_gpu} ({self.gpu_vendor})"
        )
    
    def _detect_gpu(self) -> Dict[str, any]:
        """Detect GPU and VRAM information.
        
        Returns:
            Dictionary with has_gpu, vendor, vram_gb, model keys.
        """
        gpu_info = {
            "has_gpu": False,
            "vendor": None,
            "vram_gb": 0,
            "model": None
        }
        
        system = platform.system()
        
        # Try NVIDIA first
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total,name", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[0].split(',')
                    if len(parts) >= 2:
                        vram_mb = float(parts[0].strip())
                        gpu_info["has_gpu"] = True
                        gpu_info["vendor"] = "NVIDIA"
                        gpu_info["vram_gb"] = round(vram_mb / 1024, 1)
                        gpu_info["model"] = parts[1].strip()
                        return gpu_info
        except Exception:
            pass
        
        # Try AMD ROCm
        try:
            result = subprocess.run(
                ["rocm-smi", "--showmeminfo", "vram"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "GPU" in result.stdout:
                gpu_info["has_gpu"] = True
                gpu_info["vendor"] = "AMD"
                gpu_info["vram_gb"] = 8  # Default estimate
                return gpu_info
        except Exception:
            pass
        
        # Check for Apple Silicon
        if system == "Darwin":
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and "Apple" in result.stdout:
                    gpu_info["has_gpu"] = True
                    gpu_info["vendor"] = "Apple"
                    gpu_info["model"] = result.stdout.strip()
                    
                    # Estimate unified memory
                    mem_result = subprocess.run(
                        ["sysctl", "-n", "hw.memsize"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if mem_result.returncode == 0:
                        total_mem_gb = int(mem_result.stdout.strip()) / (1024**3)
                        # Estimate ~60% available for GPU on Apple Silicon
                        gpu_info["vram_gb"] = round(total_mem_gb * 0.6, 1)
                    else:
                        gpu_info["vram_gb"] = 8  # Default
                    
                    return gpu_info
            except Exception:
                pass
        
        return gpu_info
    
    def _get_vram_tier(self) -> str:
        """Determine VRAM tier based on available memory.
        
        Returns:
            "high", "mid", or "low" tier string.
        """
        if self.vram_gb >= 12:
            return "high"
        elif self.vram_gb >= 8:
            return "mid"
        else:
            return "low"
    
    def get_recommendations(
        self, 
        task_type: TaskType = TaskType.GENERAL
    ) -> List[ModelRecommendation]:
        """Get ranked model recommendations for a task.
        
        Args:
            task_type: Type of task to optimize for.
        
        Returns:
            List of ModelRecommendation objects in priority order.
        """
        tier = self._get_vram_tier()
        return self.RECOMMENDATIONS[tier][task_type]
    
    def select_model(
        self,
        task_type: TaskType = TaskType.GENERAL,
        check_availability: bool = True
    ) -> str:
        """Select the best available model for a task.
        
        Args:
            task_type: Type of task to optimize for.
            check_availability: If True, verify model exists in Ollama.
        
        Returns:
            Model name string (e.g., "qwen2.5-coder:32b").
        """
        recommendations = self.get_recommendations(task_type)
        
        if not check_availability:
            # Return top recommendation without checking
            return recommendations[0].name
        
        # Check which models are available
        available_models = self._list_available_models()
        
        # Find first available model
        for rec in recommendations:
            if rec.name in available_models:
                logger.info(
                    f"Selected {rec.name} for {task_type.value} "
                    f"(quality: {rec.quality}, speed: {rec.speed})"
                )
                return rec.name
        
        # If no recommended models available, return first recommendation
        # (user will need to pull it)
        logger.warning(
            f"No recommended models available for {task_type.value}. "
            f"Recommend pulling: {recommendations[0].name}"
        )
        return recommendations[0].name
    
    def _list_available_models(self) -> List[str]:
        """List models available in local Ollama instance.
        
        Returns:
            List of model names.
        """
        try:
            # Import httpx here as it's an optional dependency for this feature
            import httpx
            response = httpx.get(
                f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.debug(f"Could not list Ollama models: {e}")
        
        return []
    
    def print_recommendations(self, task_type: TaskType = TaskType.GENERAL) -> None:
        """Print formatted recommendations to console.
        
        Args:
            task_type: Type of task to show recommendations for.
        """
        tier = self._get_vram_tier()
        recommendations = self.get_recommendations(task_type)
        
        print(f"\n{'='*70}")
        print(f"Model Recommendations for {task_type.value.replace('_', ' ').title()}")
        print(f"Hardware: {self.vram_gb}GB VRAM ({tier} tier)")
        print(f"{'='*70}\n")
        
        for i, rec in enumerate(recommendations, 1):
            task_badge = " [TASK-OPTIMIZED]" if rec.task_optimized else ""
            print(f"{i}. {rec.name}{task_badge}")
            print(f"   Size: {rec.size_gb}GB | Quality: {rec.quality} | Speed: {rec.speed}")
            print(f"   {rec.description}\n")
