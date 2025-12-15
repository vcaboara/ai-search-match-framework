#!/usr/bin/env python3
"""
Ollama Setup Script for AI Search Match Framework.

This script helps configure Ollama for local LLM inference by:
- Detecting GPU and VRAM
- Recommending optimal models
- Pulling selected models
- Creating/updating .env configuration
- Verifying installation
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class Colors:
    """Terminal colors for output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str) -> None:
    """Print colored header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, timeout=300)
            return result.returncode, "", ""
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_ollama_installed() -> bool:
    """Check if Ollama is installed."""
    print_info("Checking Ollama installation...")
    
    returncode, stdout, stderr = run_command(["ollama", "--version"])
    
    if returncode == 0:
        version = stdout.strip()
        print_success(f"Ollama is installed: {version}")
        return True
    else:
        print_error("Ollama is not installed")
        return False


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    print_info("Checking if Ollama is running...")
    
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        if response.status_code == 200:
            print_success("Ollama service is running")
            return True
        else:
            print_warning("Ollama service responded with unexpected status")
            return False
    except ImportError:
        print_warning("httpx not installed, skipping service check")
        return True  # Assume it's running
    except Exception as e:
        print_error(f"Ollama service is not running: {e}")
        return False


def detect_gpu() -> Dict[str, any]:
    """Detect GPU and VRAM information."""
    print_info("Detecting GPU hardware...")
    
    gpu_info = {
        "has_gpu": False,
        "vendor": None,
        "vram_gb": 0,
        "model": None
    }
    
    system = platform.system()
    
    # Try NVIDIA first
    returncode, stdout, stderr = run_command(["nvidia-smi", "--query-gpu=memory.total,name", "--format=csv,noheader,nounits"])
    if returncode == 0 and stdout.strip():
        lines = stdout.strip().split('\n')
        if lines:
            parts = lines[0].split(',')
            if len(parts) >= 2:
                try:
                    vram_mb = float(parts[0].strip())
                    gpu_info["has_gpu"] = True
                    gpu_info["vendor"] = "NVIDIA"
                    gpu_info["vram_gb"] = round(vram_mb / 1024, 1)
                    gpu_info["model"] = parts[1].strip()
                    print_success(f"Detected: {gpu_info['model']} ({gpu_info['vram_gb']} GB VRAM)")
                    return gpu_info
                except ValueError:
                    pass
    
    # Try AMD ROCm
    returncode, stdout, stderr = run_command(["rocm-smi", "--showmeminfo", "vram"])
    if returncode == 0 and "GPU" in stdout:
        gpu_info["has_gpu"] = True
        gpu_info["vendor"] = "AMD"
        gpu_info["vram_gb"] = 8  # Default estimate
        print_success(f"Detected AMD GPU (ROCm available)")
        return gpu_info
    
    # Check for Apple Silicon
    if system == "Darwin":
        returncode, stdout, stderr = run_command(["sysctl", "-n", "machdep.cpu.brand_string"])
        if returncode == 0 and "Apple" in stdout:
            gpu_info["has_gpu"] = True
            gpu_info["vendor"] = "Apple"
            gpu_info["model"] = stdout.strip()
            
            # Estimate unified memory (simplified)
            returncode, mem_out, _ = run_command(["sysctl", "-n", "hw.memsize"])
            if returncode == 0:
                try:
                    total_mem_gb = int(mem_out.strip()) / (1024**3)
                    # Estimate ~60% available for GPU on Apple Silicon
                    gpu_info["vram_gb"] = round(total_mem_gb * 0.6, 1)
                except ValueError:
                    gpu_info["vram_gb"] = 8  # Default
            
            print_success(f"Detected: {gpu_info['model']} (~{gpu_info['vram_gb']} GB unified memory)")
            return gpu_info
    
    # No GPU detected
    print_warning("No GPU detected, will use CPU inference")
    return gpu_info


def recommend_models(vram_gb: float, has_gpu: bool) -> List[Dict[str, str]]:
    """Recommend models based on hardware."""
    print_info(f"Recommending models for {vram_gb}GB VRAM (GPU: {has_gpu})...")
    
    recommendations = []
    
    if vram_gb >= 12:
        print_success("High-end hardware detected!")
        recommendations = [
            {
                "name": "qwen2.5:32b-q4",
                "size": "~20GB",
                "quality": "Excellent",
                "speed": "2-5 tok/s",
                "description": "Best quality for document analysis"
            },
            {
                "name": "qwen2.5:14b-q4",
                "size": "~9GB",
                "quality": "Very Good",
                "speed": "5-10 tok/s",
                "description": "Faster alternative, still high quality"
            },
            {
                "name": "qwen2.5-coder:32b",
                "size": "~20GB",
                "quality": "Excellent",
                "speed": "2-5 tok/s",
                "description": "Specialized for code analysis"
            }
        ]
    elif vram_gb >= 8:
        print_success("Mid-range hardware detected!")
        recommendations = [
            {
                "name": "qwen2.5:14b-q4",
                "size": "~9GB",
                "quality": "Very Good",
                "speed": "5-10 tok/s",
                "description": "Best balance of quality and speed"
            },
            {
                "name": "llama3.2:3b",
                "size": "~2GB",
                "quality": "Good",
                "speed": "10-20 tok/s",
                "description": "Faster, lighter alternative"
            },
            {
                "name": "mistral:7b-q4",
                "size": "~4GB",
                "quality": "Good",
                "speed": "8-15 tok/s",
                "description": "General purpose model"
            }
        ]
    else:
        print_warning("Limited hardware detected, recommending lightweight models")
        recommendations = [
            {
                "name": "llama3.2:3b",
                "size": "~2GB",
                "quality": "Good",
                "speed": "10-20 tok/s (GPU), 2-5 tok/s (CPU)",
                "description": "Best for limited hardware"
            },
            {
                "name": "qwen2.5:7b-q4",
                "size": "~4GB",
                "quality": "Good",
                "speed": "5-10 tok/s (GPU), 1-3 tok/s (CPU)",
                "description": "Higher quality, slower"
            },
            {
                "name": "phi3:mini",
                "size": "~2GB",
                "quality": "Good",
                "speed": "10-15 tok/s",
                "description": "Efficient Microsoft model"
            }
        ]
    
    return recommendations


def list_available_models() -> List[str]:
    """List models already pulled in Ollama."""
    print_info("Checking available models...")
    
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            if models:
                print_success(f"Found {len(models)} installed models:")
                for model in models:
                    print(f"  • {model}")
            else:
                print_warning("No models installed yet")
            return models
        else:
            print_warning("Could not retrieve model list")
            return []
    except ImportError:
        print_warning("httpx not installed, skipping model list")
        return []
    except Exception as e:
        print_warning(f"Could not list models: {e}")
        return []


def pull_model(model_name: str) -> bool:
    """Pull a model from Ollama registry."""
    print_info(f"Pulling model: {model_name}")
    print_info("This may take several minutes depending on model size and network speed...")
    
    returncode, stdout, stderr = run_command(["ollama", "pull", model_name], capture_output=False)
    
    if returncode == 0:
        print_success(f"Successfully pulled {model_name}")
        return True
    else:
        print_error(f"Failed to pull {model_name}")
        return False


def create_env_file(model_name: str, prefer_local: bool = True) -> bool:
    """Create or update .env file with Ollama configuration."""
    print_info("Creating/updating .env file...")
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    # Read existing .env or start from .env.example
    env_lines = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    elif env_example.exists():
        with open(env_example, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add Ollama configuration
    ollama_config = {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_TIMEOUT": "5.0",
        "OLLAMA_MODEL": model_name,
        "PREFER_LOCAL": str(prefer_local).lower()
    }
    
    new_lines = []
    updated_keys = set()
    
    for line in env_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            key = stripped.split('=')[0]
            if key in ollama_config:
                new_lines.append(f"{key}={ollama_config[key]}\n")
                updated_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add missing keys
    if updated_keys != set(ollama_config.keys()):
        new_lines.append("\n# Ollama Configuration (added by setup script)\n")
        for key, value in ollama_config.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}\n")
    
    # Write updated .env
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print_success(f"Updated {env_file}")
    return True


def verify_installation() -> bool:
    """Verify Ollama setup is working."""
    print_info("Verifying installation...")
    
    try:
        import httpx
        
        # Test connection
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        if response.status_code != 200:
            print_error("Cannot connect to Ollama service")
            return False
        
        # Check models
        data = response.json()
        models = data.get("models", [])
        if not models:
            print_warning("No models installed")
            return False
        
        print_success("Ollama is properly configured!")
        
        # Test inference with first model
        print_info("Testing inference...")
        model_name = models[0]["name"]
        
        test_response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": "Say 'Hello from Ollama!' and nothing else.",
                "stream": False
            },
            timeout=30.0
        )
        
        if test_response.status_code == 200:
            result = test_response.json()
            response_text = result.get("response", "").strip()
            print_success(f"Test inference successful: {response_text[:50]}...")
            return True
        else:
            print_warning("Model inference test failed")
            return False
            
    except ImportError:
        print_warning("httpx not installed, skipping verification")
        print_info("Install httpx to enable verification: pip install httpx")
        return True
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False


def interactive_setup() -> None:
    """Run interactive setup process."""
    print_header("Ollama Setup for AI Search Match Framework")
    
    # Step 1: Check Ollama installation
    if not check_ollama_installed():
        print_error("Please install Ollama first:")
        print_info("  Windows/Mac: https://ollama.ai/download")
        print_info("  Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        sys.exit(1)
    
    # Step 2: Check if service is running
    if not check_ollama_running():
        print_warning("Ollama service is not running")
        print_info("Please start Ollama:")
        system = platform.system()
        if system == "Darwin":
            print_info("  macOS: Launch Ollama.app from Applications")
        elif system == "Linux":
            print_info("  Linux: sudo systemctl start ollama")
        else:
            print_info("  Windows: Ollama should start automatically")
        
        response = input("\nPress Enter once Ollama is running, or 'q' to quit: ")
        if response.lower() == 'q':
            sys.exit(0)
        
        if not check_ollama_running():
            print_error("Still cannot connect to Ollama")
            sys.exit(1)
    
    # Step 3: Detect hardware
    gpu_info = detect_gpu()
    
    # Step 4: Ask about task type for better recommendations
    print("\n" + "="*70)
    print("What will you primarily use the model for?".center(70))
    print("="*70)
    print("\n1. Code review & analysis (qwen2.5-coder models)")
    print("2. Document analysis (patents, grants, contracts)")
    print("3. General purpose (mixed tasks)")
    print("4. Show all hardware-based recommendations")
    
    task_choice = input("\nYour choice (1-4) [4]: ").strip() or "4"
    
    if task_choice == "4":
        # Original behavior - show hardware-based recommendations
        recommendations = recommend_models(gpu_info["vram_gb"], gpu_info["has_gpu"])
    else:
        # Use ModelSelector for task-specific recommendations
        try:
            from asmf.llm import ModelSelector, TaskType
            
            selector = ModelSelector(vram_gb=gpu_info["vram_gb"])
            
            task_map = {
                "1": TaskType.CODE_REVIEW,
                "2": TaskType.DOCUMENT_ANALYSIS,
                "3": TaskType.GENERAL
            }
            
            if task_choice in task_map:
                task_type = task_map[task_choice]
                model_recs = selector.get_recommendations(task_type)
                
                # Convert to legacy format for display
                recommendations = []
                for rec in model_recs:
                    task_badge = " [TASK-OPTIMIZED]" if rec.task_optimized else ""
                    recommendations.append({
                        "name": rec.name + task_badge,
                        "size": f"{rec.size_gb}GB",
                        "quality": rec.quality,
                        "speed": rec.speed,
                        "description": rec.description
                    })
                
                print_success(f"\nTask-specific recommendations for {task_type.value.replace('_', ' ')}")
            else:
                # Fallback to hardware-based
                recommendations = recommend_models(gpu_info["vram_gb"], gpu_info["has_gpu"])
        except ImportError:
            # ASMF not installed yet, use legacy recommendations
            print_warning("ModelSelector not available, using hardware-based recommendations")
            recommendations = recommend_models(gpu_info["vram_gb"], gpu_info["has_gpu"])
    
    print("\n" + "="*70)
    print("Recommended Models:".center(70))
    print("="*70)
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['name']}")
        print(f"   Size: {rec['size']} | Quality: {rec['quality']} | Speed: {rec['speed']}")
        print(f"   {rec['description']}")
    print("="*70)
    
    # Step 5: Check existing models
    existing_models = list_available_models()
    
    # Step 6: User selection
    print("\nWhat would you like to do?")
    print("  1-{}: Pull recommended model".format(len(recommendations)))
    print("  s: Skip model installation")
    print("  q: Quit")
    
    choice = input("\nYour choice: ").strip().lower()
    
    if choice == 'q':
        sys.exit(0)
    elif choice == 's':
        if not existing_models:
            print_warning("No models installed, you'll need to pull a model manually")
            print_info("Run: ollama pull <model-name>")
        selected_model = existing_models[0] if existing_models else "qwen2.5:14b-q4"
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(recommendations):
                model_to_pull = recommendations[idx]["name"]
                # Strip task badge if present
                model_to_pull = model_to_pull.replace(" [TASK-OPTIMIZED]", "")
                if pull_model(model_to_pull):
                    selected_model = model_to_pull
                else:
                    print_error("Failed to pull model")
                    sys.exit(1)
            else:
                print_error("Invalid choice")
                sys.exit(1)
        except ValueError:
            print_error("Invalid input")
            sys.exit(1)
    
    # Step 7: Configure environment
    prefer_local = input("\nPrefer local Ollama over cloud providers? (Y/n): ").strip().lower()
    prefer_local = prefer_local != 'n'
    
    create_env_file(selected_model, prefer_local)
    
    # Step 8: Verify installation
    if verify_installation():
        print_header("Setup Complete!")
        print_success("Ollama is configured and ready to use")
        print_info("\nNext steps:")
        print_info("  1. Review your .env file")
        print_info("  2. Test with: python -c \"from asmf.providers import OllamaProvider; print(OllamaProvider().is_available())\"")
        print_info("  3. See docs/OLLAMA_SETUP.md for usage examples")
    else:
        print_warning("Setup completed but verification failed")
        print_info("Check docs/OLLAMA_SETUP.md for troubleshooting")


def main():
    """Main entry point."""
    try:
        interactive_setup()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
