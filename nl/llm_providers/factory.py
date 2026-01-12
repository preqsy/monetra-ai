from nl.llm_providers.base import LLMProvider
from nl.llm_providers.groq_provider import GroqProvider
from nl.llm_providers.ollama_provider import OllamaProvider


def get_llm_provider(temperature: float, llm_provider: str = "ollama") -> LLMProvider:
    if llm_provider == "ollama":
        # For local development and to reduce cloud cost
        return OllamaProvider(temperature=temperature)
    elif llm_provider == "groq":
        # For prod.... TODO: Use a better free LLM Model.
        return GroqProvider(temperature=temperature)
    else:
        raise
