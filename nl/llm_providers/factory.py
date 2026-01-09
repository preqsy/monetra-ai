from nl.llm_providers.base import LLMProvider
from nl.llm_providers.groq_provider import GroqProvider
from nl.llm_providers.ollama_provider import OllamaProvider


def get_llm_provider(temperature: float, llm_provider: str = "ollama") -> LLMProvider:
    if llm_provider == "ollama":
        return OllamaProvider(temperature=temperature)
    elif llm_provider == "groq":
        return GroqProvider(temperature=temperature)
    else:
        return OllamaProvider(temperature=temperature)
