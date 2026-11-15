
"""Local LLM interface for FlameBound using Ollama."""

import httpx


class OllamaClient:
    """Communicate with a locally running Ollama model."""

    def __init__(
        self,
        model="llama3.2",
        base_url="http://localhost:11434",
        timeout=120.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, prompt, system=None):
        """Generate a response from the local language model."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()
            result = response.json()

            return result["response"]

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure Ollama is running."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Ollama returned HTTP {exc.response.status_code}"
            ) from exc
