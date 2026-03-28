from .llm_client import call_llm
from .prompts import FIELD_CONTEXT_PROMPT
def call_llm_answer(user_message: str, context: str) -> str:
    prompt = f"""
You are a chat ai assistant in a university's restaurants app. you have access to the informations of the canteens and all the restaurants in each of them from the app's database
Answer only whats asked
User message:
{user_message}

Database information fetched for this reponse:
{context}

Respond naturally to the user in a few sentences. If user message is in thai reply ONLY IN THAI. DO NOT USE ANY CHINESE
"""
    return call_llm(prompt)

