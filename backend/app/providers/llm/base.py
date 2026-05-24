from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Optional

Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: Role
    content: str


@dataclass
class LLMResponse:
    text: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    raw: Optional[dict[str, Any]] = None


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    async def embed(self, texts: list[str], *, model: Optional[str] = None) -> list[list[float]]:
        raise NotImplementedError
