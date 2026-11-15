
from ai.llm.ollama_client import OllamaClient


client = OllamaClient()

answer = client.generate(
    "Explain why oxygen concentration matters "
    "in solid-fuel combustion under microgravity."
)

print("\nFLAMEBOUND AI RESPONSE:\n")
print(answer)
