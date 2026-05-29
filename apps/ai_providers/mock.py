from .base import AIResponse, BaseAIProvider


class MockAIProvider(BaseAIProvider):
    provider_name = "mock"
    model_name = "mock-localtrip-v1"

    def generate_plan(self, prompt: str) -> AIResponse:
        content = "\n".join(
            [
                "【モック生成プラン】",
                "この結果は外部AI APIを呼び出さずに生成したダミーの観光プランです。",
                "",
                "午前: 条件に合う主要スポットを1〜2か所巡ります。",
                "昼: 地域のグルメや休憩しやすい場所を組み込みます。",
                "午後: 移動負担を抑えながら、追加の観光スポットを訪問します。",
                "",
                "【生成に使ったプロンプトの冒頭】",
                prompt[:500],
            ]
        )
        return AIResponse(
            provider=self.provider_name,
            content=content,
            model_name=self.model_name,
            raw_response={"mock": True, "prompt_length": len(prompt)},
        )
