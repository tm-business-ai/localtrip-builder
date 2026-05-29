from django.conf import settings
from google import genai

from .base import AIResponse, BaseAIProvider


class GeminiProvider(BaseAIProvider):
    provider_name = "gemini"

    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL_NAME

    def _has_valid_api_key(self) -> bool:
        if not self.api_key:
            return False
        return not self.api_key.startswith("dummy-")

    def generate_plan(self, prompt: str) -> AIResponse:
        if not self._has_valid_api_key():
            raise ValueError(
                "Gemini APIキーが設定されていません。GEMINI_API_KEY を .env に設定してください。"
            )

        if not prompt or not prompt.strip():
            raise ValueError("Geminiに送信するプロンプトが空です。")

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        content = getattr(response, "text", "") or ""

        if not content.strip():
            raise ValueError("Gemini APIから空の応答が返されました。")

        return AIResponse(
            provider=self.provider_name,
            content=content,
            model_name=self.model_name,
            raw_response={"text": content},
        )
