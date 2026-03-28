import requests
import os

OLLAMA_URL = os.environ["OLLAMA_URL"] + "/api/generate"
# change for local test
MODEL = "qwen2.5:14b-instruct"

def call_llm(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": 0
        },
        timeout=100
    )

    response.raise_for_status()
    text = response.json()["response"]

    print("\n===== LLM RESPONSE =====")
    print(text)
    print("========================")

    return text
