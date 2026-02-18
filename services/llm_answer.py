from .llm_client import call_llm
from .prompts import FIELD_CONTEXT_PROMPT
def call_llm_answer(user_message: str, context: str) -> str:
    prompt = f"""
User message:
{user_message}

Database information:
{context}

Respond naturally to the user.
"""
    return call_llm(prompt)

