"""Tests for AI provider implementations."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from asmf.providers import BaseAIProvider, GeminiProvider, OllamaProvider, AIProviderFactory


class TestBaseAIProvider:
    """Test base provider interface."""

    def test_format_prompt_with_context(self):
        """Test context formatting helper."""
        # Create a concrete implementation for testing
        class TestProvider(BaseAIProvider):
            def analyze_text(self, prompt, context=None):
                return self._format_prompt_with_context(prompt, context)
            
            def is_available(self):
                return True
        
        provider = TestProvider()
        
        # Without context
        result = provider.analyze_text("Test prompt")
        assert result == "Test prompt"
        
        # With context
        context = {"doc": "Sample document", "task": "analyze"}
        result = provider.analyze_text("Test prompt", context)
        assert "doc: Sample document" in result
        assert "task: analyze" in result
        assert "Test prompt" in result


class TestGeminiProvider:
    """Test Gemini AI provider."""

    def test_init_without_api_key(self):
        """Test initialization fails gracefully without API key."""
        with patch.dict("os.environ", {}, clear=True):
            provider = GeminiProvider()
            assert not provider.is_available()

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_init_with_api_key(self, mock_model, mock_configure):
        """Test successful initialization with API key."""
        provider = GeminiProvider(api_key="test_key")
        mock_configure.assert_called_once_with(api_key="test_key")
        mock_model.assert_called_once()

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_analyze_text(self, mock_model_class, mock_configure):
        """Test text analysis."""
        # Setup mock
        mock_response = Mock()
        mock_response.text = "Analysis result"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        provider = GeminiProvider(api_key="test_key")
        result = provider.analyze_text("Test prompt")
        
        assert result == "Analysis result"
        mock_model.generate_content.assert_called_once()

    def test_analyze_empty_prompt_raises(self):
        """Test that empty prompt raises ValueError."""
        provider = GeminiProvider(api_key="test_key")
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.analyze_text("")


class TestOllamaProvider:
    """Test Ollama local AI provider."""

    @patch("httpx.get")
    def test_init_checks_availability(self, mock_get):
        """Test initialization checks Ollama availability."""
        mock_get.return_value = Mock(status_code=200)
        provider = OllamaProvider()
        assert provider.is_available()
        mock_get.assert_called_once()

    @patch("httpx.get")
    def test_init_handles_unavailable(self, mock_get):
        """Test initialization handles unavailable Ollama."""
        mock_get.side_effect = Exception("Connection refused")
        provider = OllamaProvider()
        assert not provider.is_available()

    @patch("httpx.get")
    @patch("httpx.post")
    def test_analyze_text(self, mock_post, mock_get):
        """Test text analysis."""
        # Setup availability check
        mock_get.return_value = Mock(status_code=200)
        
        # Setup analysis response
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Analysis result"}
        mock_post.return_value = mock_response
        
        provider = OllamaProvider()
        result = provider.analyze_text("Test prompt")
        
        assert result == "Analysis result"
        mock_post.assert_called_once()


class TestAIProviderFactory:
    """Test provider factory with fallback."""

    @patch("asmf.providers.provider_factory.GeminiProvider")
    def test_creates_gemini_first_by_default(self, mock_gemini):
        """Test factory tries Gemini first by default."""
        mock_instance = Mock()
        mock_instance.is_available.return_value = True
        mock_gemini.return_value = mock_instance
        
        provider = AIProviderFactory.create_provider()
        assert provider == mock_instance

    @patch("asmf.providers.provider_factory.OllamaProvider")
    @patch("asmf.providers.provider_factory.GeminiProvider")
    def test_falls_back_to_ollama(self, mock_gemini, mock_ollama):
        """Test factory falls back to Ollama if Gemini unavailable."""
        # Gemini unavailable
        mock_gemini_instance = Mock()
        mock_gemini_instance.is_available.return_value = False
        mock_gemini.return_value = mock_gemini_instance
        
        # Ollama available
        mock_ollama_instance = Mock()
        mock_ollama_instance.is_available.return_value = True
        mock_ollama.return_value = mock_ollama_instance
        
        provider = AIProviderFactory.create_provider()
        assert provider == mock_ollama_instance

    @patch("asmf.providers.provider_factory.OllamaProvider")
    def test_prefer_local_tries_ollama_first(self, mock_ollama):
        """Test factory tries Ollama first when prefer_local=True."""
        mock_instance = Mock()
        mock_instance.is_available.return_value = True
        mock_ollama.return_value = mock_instance
        
        provider = AIProviderFactory.create_provider(prefer_local=True)
        assert provider == mock_instance

    @patch("asmf.providers.provider_factory.OllamaProvider")
    @patch("asmf.providers.provider_factory.GeminiProvider")
    def test_raises_if_no_providers_available(self, mock_gemini, mock_ollama):
        """Test factory raises RuntimeError if no providers available."""
        # Both unavailable
        for mock_cls in [mock_gemini, mock_ollama]:
            mock_instance = Mock()
            mock_instance.is_available.return_value = False
            mock_cls.return_value = mock_instance
        
        with pytest.raises(RuntimeError, match="No AI providers available"):
            AIProviderFactory.create_provider()
