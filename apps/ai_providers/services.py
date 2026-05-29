from .base import AIResponse
from .factory import get_ai_provider


class EmptyAIPromptError(ValueError):
    pass


def generate_travel_plan(prompt: str, provider_name: str = "mock") -> AIResponse:
    if not prompt.strip():
        raise EmptyAIPromptError("AIに渡すプロンプトが空です。")

    provider = get_ai_provider(provider_name)
    return provider.generate_plan(prompt)


def generate_travel_plan_with_ai(
    plan_request,
    provider_name: str = "mock",
) -> AIResponse:
    prompt = plan_request.ai_prompt_preview
    if not prompt.strip():
        raise EmptyAIPromptError("旅行プラン作成依頼にAIプロンプト下書きがありません。")

    provider = get_ai_provider(provider_name)
    return provider.generate_plan(prompt)
