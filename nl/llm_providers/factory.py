from nl.llm_providers.base import LLMProvider


def get_llm_provider(temperature: float, llm_provider: str = "ollama") -> LLMProvider:
    if llm_provider == "ollama":
        from nl.llm_providers.ollama_provider import OllamaProvider

        # For local development and to reduce cloud cost
        return OllamaProvider(temperature=temperature)
    elif llm_provider == "groq":
        from nl.llm_providers.groq_provider import GroqProvider

        # For prod.... TODO: Use a better free LLM Model.
        return GroqProvider(temperature=temperature)
    else:
        raise
