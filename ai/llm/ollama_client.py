"""Compatibility facade over centralized Ollama settings and provider adapter."""

from ai.config import AISettings
from ai.providers import OllamaProvider


class OllamaClient:
    def __init__(self, model: str | None = None, base_url: str | None = None, timeout: float | None = None):
        settings = AISettings.from_env()
        if model is not None or base_url is not None or timeout is not None:
            from dataclasses import replace
            settings = replace(
                settings,
                generation_model=model or settings.generation_model,
                ollama_base_url=(base_url or settings.ollama_base_url).rstrip("/"),
                request_timeout_seconds=timeout or settings.request_timeout_seconds,
            )
        self.settings = settings
        self.provider = OllamaProvider(settings)

    def chat(self, messages, *, tools=None, response_format=None):
        return self.provider.chat(messages, tools=tools, response_format=response_format)

    def generate(self, prompt, system=None):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.provider.chat(messages)["content"]
