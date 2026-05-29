from django.conf import settings
from openai import OpenAI

from .base import AIResponse, BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    provider_name = "openai"

    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key if api_key is not None else settings.OPENAI_API_KEY
        self.model_name = model_name or settings.OPENAI_MODEL_NAME

    def _has_valid_api_key(self) -> bool:
        if not self.api_key:
            return False
        return not self.api_key.startswith("dummy-")

    def generate_plan(self, prompt: str) -> AIResponse:
        if not self._has_valid_api_key():
            raise ValueError(
                "OpenAI APIキーが設定されていません。OPENAI_API_KEY を .env に設定してください。"
            )

        if not prompt or not prompt.strip():
            raise ValueError("OpenAIに送信するプロンプトが空です。")

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model_name,
            input=prompt,
        )
        content = getattr(response, "output_text", "") or ""

        if not content.strip():
            raise ValueError("OpenAI APIから空の応答が返されました。")

        return AIResponse(
            provider=self.provider_name,
            content=content,
            model_name=self.model_name,
            raw_response={"text": content},
        )
