from .llm_client import call_llm
from .prompts import FIELD_CONTEXT_PROMT
def call_llm_answer(user_message: str, context: str) -> str:
    prompt = f"""
User message:
{user_message}

Database information:
{context}
{FIELD_CONTEXT_PROMT}
Respond naturally to the user, FOCUS on user's message context.
you shouldnt generate anymore than a few senctences
"""
    return call_llm(prompt)

