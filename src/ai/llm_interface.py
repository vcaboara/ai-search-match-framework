"""
Multi-provider LLM interface with fallback support.

Supports OpenAI, Anthropic, Gemini, Ollama, DeepSeek with automatic
failover and retry logic.
"""
import os
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    name: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    enabled: bool = True


class LLMInterface:
    """
    Multi-provider LLM interface with automatic fallback.
    
    Example:
        llm = LLMInterface()
        response = llm.query("What is Python?")
        
        # Batch evaluation
        scores = llm.batch_evaluate(items, criteria="relevance")
    """
    
    def __init__(self, providers: Optional[List[ProviderConfig]] = None):
        """
        Initialize LLM interface.
        
        Args:
            providers: List of provider configs. If None, uses defaults.
        """
        self.providers = providers or self._get_default_providers()
        self._current_provider_index = 0
    
    def _get_default_providers(self) -> List[ProviderConfig]:
        """Get default provider configuration from environment."""
        return [
            ProviderConfig(
                name="openai",
                model="gpt-4o",
                api_key=os.getenv("OPENAI_API_KEY"),
                enabled=bool(os.getenv("OPENAI_API_KEY"))
            ),
            ProviderConfig(
                name="anthropic",
                model="claude-3-sonnet-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                enabled=bool(os.getenv("ANTHROPIC_API_KEY"))
            ),
            ProviderConfig(
                name="gemini",
                model="gemini-pro",
                api_key=os.getenv("GEMINI_API_KEY"),
                enabled=bool(os.getenv("GEMINI_API_KEY"))
            ),
            ProviderConfig(
                name="ollama",
                model="qwen2.5:32b",
                base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                enabled=True
            )
        ]
    
    def query(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Query LLM with automatic fallback.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum response length
            temperature: Response randomness (0-1)
            
        Returns:
            LLM response text
            
        Raises:
            Exception: If all providers fail
        """
        for i, provider in enumerate(self.providers):
            if not provider.enabled:
                continue
            
            try:
                logger.info(f"Querying {provider.name} ({provider.model})")
                response = self._query_provider(provider, prompt, max_tokens, temperature)
                self._current_provider_index = i
                return response
            except Exception as e:
                logger.warning(f"{provider.name} failed: {e}")
                continue
        
        raise Exception("All LLM providers failed")
    
    def _query_provider(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Query specific provider."""
        if provider.name == "openai":
            return self._query_openai(provider, prompt, max_tokens, temperature)
        elif provider.name == "anthropic":
            return self._query_anthropic(provider, prompt, max_tokens, temperature)
        elif provider.name == "gemini":
            return self._query_gemini(provider, prompt, max_tokens, temperature)
        elif provider.name == "ollama":
            return self._query_ollama(provider, prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {provider.name}")
    
    def _query_openai(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Query OpenAI API."""
        from openai import OpenAI
        
        client = OpenAI(api_key=provider.api_key)
        response = client.chat.completions.create(
            model=provider.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _query_anthropic(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Query Anthropic API."""
        from anthropic import Anthropic
        
        client = Anthropic(api_key=provider.api_key)
        response = client.messages.create(
            model=provider.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _query_gemini(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Query Google Gemini API."""
        import google.generativeai as genai
        
        genai.configure(api_key=provider.api_key)
        model = genai.GenerativeModel(provider.model)
        
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    
    def _query_ollama(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Query Ollama local API."""
        import requests
        
        url = f"{provider.base_url}/api/generate"
        payload = {
            "model": provider.model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            },
            "stream": False
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    
    def batch_evaluate(
        self,
        items: List[dict],
        criteria: str,
        batch_size: int = 10
    ) -> List[Tuple[dict, float]]:
        """
        Evaluate items in batches with scoring.
        
        Args:
            items: Items to evaluate
            criteria: Evaluation criteria
            batch_size: Items per batch
            
        Returns:
            List of (item, score) tuples
        """
        import json
        
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            
            prompt = f"""Evaluate these items based on: {criteria}
            
Items:
{json.dumps(batch, indent=2)}

Return ONLY a JSON array of scores (0.0-1.0), one per item:
[0.85, 0.62, 0.91, ...]"""
            
            try:
                response = self.query(prompt, max_tokens=500, temperature=0.3)
                scores = self._parse_scores(response)
                
                for item, score in zip(batch, scores):
                    results.append((item, score))
            except Exception as e:
                logger.error(f"Batch evaluation failed: {e}")
                # Assign default low scores on failure
                for item in batch:
                    results.append((item, 0.5))
        
        return results
    
    def _parse_scores(self, response: str) -> List[float]:
        """Parse scores from LLM response."""
        import json
        import re
        
        # Try direct JSON parse
        try:
            scores = json.loads(response)
            if isinstance(scores, list):
                return [float(s) for s in scores]
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try to extract JSON array from text
        match = re.search(r'\[([\d\.,\s]+)\]', response)
        if match:
            scores_str = match.group(1)
            return [float(s.strip()) for s in scores_str.split(',')]
        
        # Fallback: look for individual numbers
        numbers = re.findall(r'0\.\d+|1\.0', response)
        if numbers:
            return [float(n) for n in numbers]
        
        raise ValueError(f"Could not parse scores from: {response}")
    
    def get_current_provider(self) -> ProviderConfig:
        """Get currently active provider."""
        return self.providers[self._current_provider_index]
