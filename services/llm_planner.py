import json
from .llm_client import call_llm
from .prompts import PLANNER_PROMPT

def call_llm_planner(user_message: str) -> dict:
    prompt = PLANNER_PROMPT + user_message

    llm_output = call_llm(prompt)

    return json.loads(llm_output)
