from nl.llm_providers.base import LLMProvider
from nl.llm_providers.groq_provider import GroqProvider
from nl.llm_providers.ollama_provider import OllamaProvider


KIND = "groq"


def get_llm_provider() -> LLMProvider:
    if KIND == "ollama":
        return OllamaProvider()
    elif KIND == "groq":
        return GroqProvider()
    else:
        return OllamaProvider()
