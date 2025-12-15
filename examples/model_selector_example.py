#!/usr/bin/env python3
"""
Example: Task-Specific Model Selection with ModelSelector.

This example demonstrates how to use ASMF's ModelSelector to automatically
choose optimal Ollama models based on:
1. Your GPU VRAM capacity
2. The type of task you're performing

No more guessing which model to use!
"""

from asmf.llm import ModelSelector, TaskType
from asmf.providers import OllamaProvider


def example_1_basic_selection():
    """Example 1: Basic model selection."""
    print("="*70)
    print("Example 1: Basic Model Selection")
    print("="*70)
    
    # Create selector - automatically detects your GPU
    selector = ModelSelector()
    print(f"\nDetected: {selector.vram_gb}GB VRAM")
    print(f"GPU Vendor: {selector.gpu_vendor}")
    
    # Get best model for code review
    code_model = selector.select_model(TaskType.CODE_REVIEW, check_availability=False)
    print(f"\nBest for code review: {code_model}")
    
    # Get best model for document analysis
    doc_model = selector.select_model(TaskType.DOCUMENT_ANALYSIS, check_availability=False)
    print(f"Best for documents: {doc_model}")
    
    # Get best model for general use
    general_model = selector.select_model(TaskType.GENERAL, check_availability=False)
    print(f"Best for general use: {general_model}\n")


def example_2_view_recommendations():
    """Example 2: View all recommendations for a task."""
    print("\n" + "="*70)
    print("Example 2: View All Recommendations")
    print("="*70 + "\n")
    
    selector = ModelSelector()
    
    # Print recommendations for code review
    selector.print_recommendations(TaskType.CODE_REVIEW)


def example_3_check_availability():
    """Example 3: Check which models are available in Ollama."""
    print("\n" + "="*70)
    print("Example 3: Check Model Availability")
    print("="*70 + "\n")
    
    selector = ModelSelector()
    
    # This will check your local Ollama and select first available model
    try:
        model = selector.select_model(TaskType.CODE_REVIEW, check_availability=True)
        print(f"✓ Selected available model: {model}")
        print(f"\nTo use it:")
        print(f"  provider = OllamaProvider(model='{model}')")
    except Exception as e:
        print(f"✗ Could not connect to Ollama: {e}")
        print("\nMake sure Ollama is running:")
        print("  macOS: Launch Ollama.app")
        print("  Linux: sudo systemctl start ollama")
        print("  Windows: Ollama runs automatically")


def example_4_code_review_workflow():
    """Example 4: Complete code review workflow."""
    print("\n" + "="*70)
    print("Example 4: Code Review Workflow")
    print("="*70 + "\n")
    
    # Select best code review model
    selector = ModelSelector()
    model = selector.select_model(TaskType.CODE_REVIEW, check_availability=False)
    print(f"Using model: {model}")
    
    # Create provider (will fail if Ollama not running, that's OK for demo)
    try:
        provider = OllamaProvider(model=model)
        
        if not provider.is_available():
            print("\n⚠ Ollama not available. Would analyze with cloud provider.")
            return
        
        # Example code to review
        code_sample = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
"""
        
        print("\nCode to review:")
        print(code_sample)
        print("\nAsking AI for review...")
        
        result = provider.analyze_text(f"""
Review this Python code for:
1. Potential bugs
2. Performance issues
3. Best practice violations

Code:
{code_sample}

Provide specific suggestions for improvement.
""")
        
        print("\nAI Review:")
        print(result)
        
    except Exception as e:
        print(f"\n⚠ Could not analyze: {e}")
        print("This is expected if Ollama is not running.")


def example_5_document_analysis_workflow():
    """Example 5: Document analysis workflow."""
    print("\n" + "="*70)
    print("Example 5: Document Analysis Workflow")
    print("="*70 + "\n")
    
    # Select best document analysis model
    selector = ModelSelector()
    model = selector.select_model(TaskType.DOCUMENT_ANALYSIS, check_availability=False)
    print(f"Using model: {model}")
    
    try:
        provider = OllamaProvider(model=model)
        
        if not provider.is_available():
            print("\n⚠ Ollama not available. Would analyze with cloud provider.")
            return
        
        # Example patent abstract
        patent_text = """
A method and apparatus for pyrolysis of waste materials using microwave 
radiation. The system includes a microwave chamber with controlled 
atmosphere, temperature sensors, and automated feedstock delivery. 
The process achieves higher energy efficiency compared to conventional 
thermal pyrolysis by selective heating of materials.
"""
        
        print("\nDocument to analyze:")
        print(patent_text)
        print("\nAsking AI for analysis...")
        
        result = provider.analyze_text(f"""
Analyze this patent abstract and identify:
1. Key innovative aspects
2. Potential prior art areas to search
3. Commercial applications

Abstract:
{patent_text}

Provide a structured analysis.
""")
        
        print("\nAI Analysis:")
        print(result)
        
    except Exception as e:
        print(f"\n⚠ Could not analyze: {e}")
        print("This is expected if Ollama is not running.")


def example_6_manual_override():
    """Example 6: Manual VRAM override (testing different hardware)."""
    print("\n" + "="*70)
    print("Example 6: Manual VRAM Override")
    print("="*70 + "\n")
    
    # Simulate different hardware configurations
    configs = [
        (4.0, "Low-end GPU (4GB)"),
        (8.0, "Mid-range GPU (8GB)"),
        (16.0, "High-end GPU (16GB)")
    ]
    
    for vram, description in configs:
        print(f"\n{description}:")
        selector = ModelSelector(vram_gb=vram)
        
        # Get top recommendation for code review
        recs = selector.get_recommendations(TaskType.CODE_REVIEW)
        top_model = recs[0]
        print(f"  Best model: {top_model.name}")
        print(f"  Size: {top_model.size_gb}GB")
        print(f"  Quality: {top_model.quality}")
        print(f"  Speed: {top_model.speed}")


def example_7_all_task_types():
    """Example 7: Compare recommendations across all task types."""
    print("\n" + "="*70)
    print("Example 7: All Task Types Comparison")
    print("="*70 + "\n")
    
    selector = ModelSelector()
    print(f"Hardware: {selector.vram_gb}GB VRAM\n")
    
    for task_type in TaskType:
        recs = selector.get_recommendations(task_type)
        top_model = recs[0]
        
        task_badge = " 🎯" if top_model.task_optimized else ""
        print(f"{task_type.value.replace('_', ' ').title()}{task_badge}:")
        print(f"  → {top_model.name} ({top_model.quality}, {top_model.speed})")


def main():
    """Run all examples."""
    print("\n" + "🚀 " + "ASMF ModelSelector Examples".center(66) + " 🚀")
    
    try:
        example_1_basic_selection()
        example_2_view_recommendations()
        example_3_check_availability()
        example_4_code_review_workflow()
        example_5_document_analysis_workflow()
        example_6_manual_override()
        example_7_all_task_types()
        
        print("\n" + "="*70)
        print("✓ Examples completed!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Install a model: ollama pull qwen2.5-coder:7b")
        print("  2. Use ModelSelector in your code")
        print("  3. See docs/OLLAMA_SETUP.md for more info")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Examples interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
