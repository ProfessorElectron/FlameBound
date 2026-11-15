"""Opt-in live compatibility test: FLAMEBOUND_RUN_LIVE_OLLAMA_TESTS=1."""

import os
import unittest

from ai.config import AISettings
from ai.providers import OllamaProvider
from ai.tools import TOOL_SCHEMAS
from ai.llm.ollama_client import OllamaClient


@unittest.skipUnless(os.getenv("FLAMEBOUND_RUN_LIVE_OLLAMA_TESTS") == "1",
                     "set FLAMEBOUND_RUN_LIVE_OLLAMA_TESTS=1 to contact Ollama")
class OllamaToolCallCompatibilityTests(unittest.TestCase):
    def test_generation_model_returns_the_registered_poxygen_tool(self):
        settings = AISettings.from_env()
        provider = OllamaProvider(settings)
        message = provider.chat([
            {"role": "system", "content": "Use the provided function for the requested calculation."},
            {"role": "user", "content": "Calculate oxygen partial pressure at oxygen mole fraction 0.21 and absolute total pressure 101.325 kPa."},
        ], tools=TOOL_SCHEMAS)
        calls = message.get("tool_calls", [])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["function"]["name"], "calculate_oxygen_partial_pressure")
        self.assertEqual(calls[0]["function"]["arguments"], {
            "oxygen_mole_fraction": 0.21, "total_pressure": 101.325,
            "pressure_unit": "kPa", "pressure_basis": "absolute",
        })

    def test_generation_model_returns_the_registered_comparison_tool(self):
        settings = AISettings.from_env()
        provider = OllamaProvider(settings)
        message = provider.chat([
            {"role": "system", "content": "Use the provided comparison function. Do not infer missing values."},
            {"role": "user", "content": "Compare scenario oxygen 0.21, 101.325 kPa absolute with reference oxygen 0.18, 95 kPa absolute."},
        ], tools=TOOL_SCHEMAS)
        calls = message.get("tool_calls", [])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["function"]["name"], "compare_atmospheres")
        args = calls[0]["function"]["arguments"]
        self.assertEqual(args["scenario"]["oxygen_mole_fraction"], 0.21)
        self.assertEqual(args["reference"]["total_pressure"], 95)

if __name__ == "__main__":
    unittest.main()
