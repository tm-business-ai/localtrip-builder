from anthropic import Anthropic
from django.conf import settings

from .base import AIResponse, BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    provider_name = "anthropic"

    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key if api_key is not None else settings.ANTHROPIC_API_KEY
        self.model_name = model_name or settings.ANTHROPIC_MODEL_NAME

    def _has_valid_api_key(self) -> bool:
        if not self.api_key:
            return False
        return not self.api_key.startswith("dummy-")

    def generate_plan(self, prompt: str) -> AIResponse:
        if not self._has_valid_api_key():
            raise ValueError(
                "Claude APIキーが設定されていません。ANTHROPIC_API_KEY を .env に設定してください。"
            )

        if not prompt or not prompt.strip():
            raise ValueError("Claudeに送信するプロンプトが空です。")

        client = Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model_name,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content_parts = []
        for block in getattr(message, "content", []) or []:
            text = getattr(block, "text", "")
            if text:
                content_parts.append(text)

        content = "\n".join(content_parts).strip()

        if not content:
            raise ValueError("Claude APIから空の応答が返されました。")

        return AIResponse(
            provider=self.provider_name,
            content=content,
            model_name=self.model_name,
            raw_response={"text": content},
        )
