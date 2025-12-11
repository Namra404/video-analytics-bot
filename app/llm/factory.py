from functools import lru_cache

from app.core.config import settings
from app.llm.base import LLMClient
from app.llm.mistral_client import MistralLLMClient


@lru_cache
def get_llm_client() -> LLMClient:
    provider = settings.llm.llm_provider.lower()

    if provider == "mistral":
        return MistralLLMClient()
    raise ValueError(f"Unknown LLM_PROVIDER={provider!r}")
