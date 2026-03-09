from pydantic import BaseModel
from typing import List, Dict, Any

#====================================================================
#user table
class UserCreate(BaseModel):
    username : str
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
class RestaurantResponse(BaseModel):
    id: int
    name: str
    queue: int
    image_url: str | None
    canteen_id: int

    model_config = {
        "from_attributes": True
    }


#==========================================================================================================================
#canteen table

class CanteenResponse(BaseModel):
    id: int
    name: str
    utilization: int
    latitude: float
    longitude: float
    image_url: str | None

    model_config = {
        "from_attributes": True
    }


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