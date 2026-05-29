from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from .base import AIResponse, BaseAIProvider
from .claude import ClaudeProvider
from .factory import UnsupportedAIProviderError, get_ai_provider
from .gemini import GeminiProvider
from .mock import MockAIProvider
from .openai import OpenAIProvider
from .services import EmptyAIPromptError, generate_travel_plan, generate_travel_plan_with_ai


class AIProviderTests(SimpleTestCase):
    def test_mock_provider_implements_base_provider(self):
        provider = MockAIProvider()

        self.assertIsInstance(provider, BaseAIProvider)

    def test_mock_provider_returns_ai_response(self):
        response = MockAIProvider().generate_plan("宮崎市の日帰り観光プラン")

        self.assertIsInstance(response, AIResponse)
        self.assertEqual(response.provider, "mock")
        self.assertIn("モック生成プラン", response.content)
        self.assertEqual(response.model_name, "mock-localtrip-v1")

    def test_factory_returns_mock_provider(self):
        provider = get_ai_provider("mock")

        self.assertIsInstance(provider, MockAIProvider)

    def test_factory_returns_gemini_provider(self):
        provider = get_ai_provider("gemini")

        self.assertIsInstance(provider, GeminiProvider)

    def test_factory_returns_openai_provider(self):
        provider = get_ai_provider("openai")

        self.assertIsInstance(provider, OpenAIProvider)

    def test_factory_returns_claude_provider(self):
        provider = get_ai_provider("anthropic")

        self.assertIsInstance(provider, ClaudeProvider)

    def test_factory_rejects_unknown_provider(self):
        with self.assertRaises(UnsupportedAIProviderError):
            get_ai_provider("unknown")

    def test_generate_travel_plan_uses_mock_provider(self):
        response = generate_travel_plan("候補スポットを使って生成してください。")

        self.assertEqual(response.provider, "mock")
        self.assertIn("候補スポット", response.content)

    def test_generate_travel_plan_with_ai_uses_request_prompt(self):
        plan_request = SimpleNamespace(ai_prompt_preview="宮崎市の観光プランを作成してください。")

        response = generate_travel_plan_with_ai(plan_request)

        self.assertEqual(response.provider, "mock")
        self.assertIn("宮崎市", response.content)

    def test_generate_travel_plan_with_ai_rejects_empty_prompt(self):
        plan_request = SimpleNamespace(ai_prompt_preview="")

        with self.assertRaises(EmptyAIPromptError):
            generate_travel_plan_with_ai(plan_request)


class GeminiProviderTests(SimpleTestCase):
    @override_settings(GEMINI_API_KEY="", GEMINI_MODEL_NAME="gemini-test")
    def test_gemini_provider_requires_api_key(self):
        provider = GeminiProvider()

        with self.assertRaisesMessage(ValueError, "Gemini APIキー"):
            provider.generate_plan("旅行プランを作成してください。")

    @override_settings(GEMINI_API_KEY="dummy-gemini-api-key", GEMINI_MODEL_NAME="gemini-test")
    def test_gemini_provider_rejects_dummy_api_key(self):
        provider = GeminiProvider()

        with self.assertRaisesMessage(ValueError, "Gemini APIキー"):
            provider.generate_plan("旅行プランを作成してください。")

    @override_settings(GEMINI_API_KEY="test-gemini-api-key", GEMINI_MODEL_NAME="gemini-test")
    @patch("apps.ai_providers.gemini.genai.Client")
    def test_gemini_provider_returns_ai_response_without_real_api_call(self, client_class):
        mock_response = Mock(text="Geminiで生成した観光プラン")
        client_class.return_value.models.generate_content.return_value = mock_response

        response = GeminiProvider().generate_plan("宮崎市の観光プラン")

        self.assertEqual(response.provider, "gemini")
        self.assertEqual(response.content, "Geminiで生成した観光プラン")
        self.assertEqual(response.model_name, "gemini-test")
        client_class.return_value.models.generate_content.assert_called_once_with(
            model="gemini-test",
            contents="宮崎市の観光プラン",
        )


class OpenAIProviderTests(SimpleTestCase):
    @override_settings(OPENAI_API_KEY="", OPENAI_MODEL_NAME="gpt-test")
    def test_openai_provider_requires_api_key(self):
        provider = OpenAIProvider()

        with self.assertRaisesMessage(ValueError, "OpenAI APIキー"):
            provider.generate_plan("旅行プランを作成してください。")

    @override_settings(OPENAI_API_KEY="dummy-openai-api-key", OPENAI_MODEL_NAME="gpt-test")
    def test_openai_provider_rejects_dummy_api_key(self):
        provider = OpenAIProvider()

        with self.assertRaisesMessage(ValueError, "OpenAI APIキー"):
            provider.generate_plan("旅行プランを作成してください。")

    @override_settings(OPENAI_API_KEY="test-openai-api-key", OPENAI_MODEL_NAME="gpt-test")
    @patch("apps.ai_providers.openai.OpenAI")
    def test_openai_provider_returns_ai_response_without_real_api_call(self, client_class):
        mock_response = Mock(output_text="OpenAIで生成した観光プラン")
        client_class.return_value.responses.create.return_value = mock_response

        response = OpenAIProvider().generate_plan("宮崎市の観光プラン")

        self.assertEqual(response.provider, "openai")
        self.assertEqual(response.content, "OpenAIで生成した観光プラン")
        self.assertEqual(response.model_name, "gpt-test")
        client_class.return_value.responses.create.assert_called_once_with(
            model="gpt-test",
            input="宮崎市の観光プラン",
        )


class ClaudeProviderTests(SimpleTestCase):
    @override_settings(ANTHROPIC_API_KEY="", ANTHROPIC_MODEL_NAME="claude-test")
    def test_claude_provider_requires_api_key(self):
        provider = ClaudeProvider()

        with self.assertRaisesMessage(ValueError, "Claude APIキー"):
            provider.generate_plan("旅行プランを作成してください。")

    @override_settings(ANTHROPIC_API_KEY="dummy-anthropic-api-key", ANTHROPIC_MODEL_NAME="claude-test")
    def test_claude_provider_rejects_dummy_api_key(self):
        provider = ClaudeProvider()

        with self.assertRaisesMessage(ValueError, "Claude APIキー"):
            provider.generate_plan("旅行プランを作成してください。")

    @override_settings(ANTHROPIC_API_KEY="test-anthropic-api-key", ANTHROPIC_MODEL_NAME="claude-test")
    @patch("apps.ai_providers.claude.Anthropic")
    def test_claude_provider_returns_ai_response_without_real_api_call(self, client_class):
        text_block = Mock(text="Claudeで生成した観光プラン")
        mock_message = Mock(content=[text_block])
        client_class.return_value.messages.create.return_value = mock_message

        response = ClaudeProvider().generate_plan("宮崎市の観光プラン")

        self.assertEqual(response.provider, "anthropic")
        self.assertEqual(response.content, "Claudeで生成した観光プラン")
        self.assertEqual(response.model_name, "claude-test")
        client_class.return_value.messages.create.assert_called_once_with(
            model="claude-test",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": "宮崎市の観光プラン",
                }
            ],
        )
