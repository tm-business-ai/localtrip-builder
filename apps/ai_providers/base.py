from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AIResponse:
    provider: str
    content: str
    model_name: str = ""
    raw_response: dict | None = None


class BaseAIProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    def generate_plan(self, prompt: str) -> AIResponse:
        pass
