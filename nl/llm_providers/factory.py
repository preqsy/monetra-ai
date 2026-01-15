from nl.llm_providers.base import LLMProvider


def get_llm_provider(temperature: float, llm_provider: str) -> LLMProvider:
    if llm_provider == "ollama":
        # For local development and to reduce cloud cost
        print(f"Using LLM Provider: {llm_provider}")

        from nl.llm_providers.ollama_provider import OllamaProvider

        return OllamaProvider(temperature=temperature)
    elif llm_provider == "groq":
        # For prod.... TODO: Use a better free LLM Model.
        print(f"Using LLM Provider: {llm_provider}")

        from nl.llm_providers.groq_provider import GroqProvider

        return GroqProvider(temperature=temperature)
    else:
        raise
