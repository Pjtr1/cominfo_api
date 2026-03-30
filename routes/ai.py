from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from database import get_db
from schemas import LLMPlannerResponse, AIMessageRequest
from services.llm_planner import call_llm_planner
from services.llm_answer import call_llm_answer
from services.function_executor import execute_function

router = APIRouter(prefix="/ai", tags=["AI"])



@router.post("/message")
def ai_message(payload: AIMessageRequest, db: Session = Depends(get_db)):
    message = payload.message
    user_lat = payload.latitude
    user_lon = payload.longitude

    # Planner decides which functions to call
    planner_json = call_llm_planner(message)
    print("PLANNER JSON PARSED:", planner_json, flush=True)

    try:
        planner = LLMPlannerResponse(**planner_json)
    except Exception as e:
        print("PLANNER PARSE ERROR:", e, flush=True)
        print("RAW PLANNER JSON:", planner_json, flush=True)
        return {"reply": "Sorry, I couldn't understand your request."}

    results = []
    for call in planner.calls:
        result = execute_function(db, call.function, call.args, user_lat, user_lon)
        results.append(result)

    context = json.dumps(results, indent=2)
    print("FULL CONTEXT SENT TO LLM:", context, flush=True)

    reply = call_llm_answer(message, context)

    return {"reply": reply}