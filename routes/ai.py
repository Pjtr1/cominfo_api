from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from database import get_db
from schemas import LLMPlannerResponse, AIMessageRequest
from services.llm_planner import call_llm_planner
from services.llm_answer import call_llm_answer
from services.function_executor import execute_function

router = APIRouter(prefix="/ai", tags=["AI"])

def serialize(obj):
    if isinstance(obj, list):
        return [serialize(o) for o in obj]
    if hasattr(obj, "__table__"):
        return {
            column.name: getattr(obj, column.name)
            for column in obj.__table__.columns
        }
    return obj

@router.post("/message")
def ai_message(payload: AIMessageRequest, db: Session = Depends(get_db)):
    message = payload.message

    planner_json = call_llm_planner(message)
    #test print
    print("PLANNER JSON PARSED:")
    print(planner_json)

    try:
        planner = LLMPlannerResponse(**planner_json)
    except Exception as e:
        print("PLANNER PARSE ERROR:", e)
        print("RAW PLANNER JSON:", planner_json)
        return {"reply": "Sorry, I couldn't understand your request."}

    results = []
    for call in planner.calls:
        results.append(
            execute_function(db, call.function, call.args)
        )

    context = serialize(results)

    reply = call_llm_answer(
        message,
        json.dumps(context, indent=2)
    )

    return {"reply": reply}
