from .base import BaseAIProvider
from .claude import ClaudeProvider
from .gemini import GeminiProvider
from .mock import MockAIProvider
from .openai import OpenAIProvider


class UnsupportedAIProviderError(ValueError):
    pass


def get_ai_provider(provider_name: str = "mock") -> BaseAIProvider:
    providers: dict[str, type[BaseAIProvider]] = {
        MockAIProvider.provider_name: MockAIProvider,
        GeminiProvider.provider_name: GeminiProvider,
        OpenAIProvider.provider_name: OpenAIProvider,
        ClaudeProvider.provider_name: ClaudeProvider,
    }

    try:
        provider_class = providers[provider_name]
    except KeyError as exc:
        raise UnsupportedAIProviderError(
            f"Unsupported AI provider: {provider_name}"
        ) from exc

    return provider_class()
