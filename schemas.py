from pydantic import BaseModel
from typing import List, Dict, Any

#====================================================================
#user table
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    email: str
    password: str

#=====================================================================================================
#restaurant table


#==========================================================================================================================
#canteen table


#=================================================================================================================
#llm(planner) output
class LLMCall(BaseModel):
    function: str
    args: Dict[str, Any]

class LLMPlannerResponse(BaseModel):
    calls: List[LLMCall]

#==================================================================================================================
#ai stuff idk
class AIMessageRequest(BaseModel):
    message: str