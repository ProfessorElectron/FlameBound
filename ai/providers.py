"""Ollama provider adapter; generation and embedding configuration stay separate."""

from __future__ import annotations

from typing import Any

import httpx

from ai.config import AISettings, ProviderError


class OllamaProvider:
    def __init__(self, settings: AISettings, client: httpx.Client | None = None):
        self.settings = settings
        self._client = client

    def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            if self._client is None:
                response = httpx.post(
                    f"{self.settings.ollama_base_url}{endpoint}",
                    json=payload,
                    timeout=self.settings.request_timeout_seconds,
                )
            else:
                response = self._client.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ProviderError("invalid_provider_response", "The model provider returned an invalid response.")
            return data
        except ProviderError:
            raise
        except httpx.TimeoutException as exc:
            raise ProviderError("provider_timeout", "The model provider timed out.", retryable=True) from exc
        except httpx.ConnectError as exc:
            raise ProviderError("provider_unavailable", "The model provider is unavailable.", retryable=True) from exc
        except httpx.HTTPStatusError as exc:
            code = "model_unavailable" if exc.response.status_code in {400, 404} else "provider_error"
            raise ProviderError(code, "The model provider rejected or failed the request.", retryable=exc.response.status_code >= 500) from exc
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise ProviderError("invalid_provider_response", "The model provider returned an invalid response.") from exc

    def chat(self, messages: list[dict[str, str]], *, tools: list[dict[str, Any]] | None = None,
             response_format: str | dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.settings.generation_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": self.settings.max_output_tokens},
        }
        # Qwen3 otherwise spends the bounded structured-response budget on its
        # private reasoning trace, which can leave the API with no JSON answer.
        if self.settings.generation_model.casefold().startswith("qwen3"):
            payload["think"] = False
        if tools:
            payload["tools"] = tools
        if response_format is not None:
            payload["format"] = response_format
        data = self._post("/api/chat", payload)
        message = data.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content", ""), str):
            raise ProviderError("invalid_provider_response", "The model provider returned an invalid chat message.")
        return message

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self.settings.embedding_model
        if not model:
            raise ProviderError("embedding_model_unconfigured", "An embedding model has not been selected.")
        data = self._post("/api/embed", {"model": model, "input": texts})
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise ProviderError("invalid_provider_response", "The embedding provider returned an invalid vector batch.")
        vectors: list[list[float]] = []
        dimension: int | None = None
        for vector in embeddings:
            if not isinstance(vector, list) or not vector:
                raise ProviderError("invalid_provider_response", "The embedding provider returned an invalid vector.")
            try:
                values = [float(value) for value in vector]
            except (TypeError, ValueError, OverflowError) as exc:
                raise ProviderError("invalid_provider_response", "The embedding provider returned an invalid vector.") from exc
            if any(not __import__("math").isfinite(value) for value in values):
                raise ProviderError("invalid_provider_response", "The embedding provider returned non-finite values.")
            dimension = dimension or len(values)
            if len(values) != dimension:
                raise ProviderError("embedding_dimension_mismatch", "Embedding dimensions changed within one batch.")
            vectors.append(values)
        return vectors
