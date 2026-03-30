from sqlalchemy.orm import Session
import crud
from services.serializer import serialize_for_llm  # import the new serialize function

def execute_function(db: Session, function: str, args: dict, user_lat=None, user_lon=None):
    if function == "get_canteens":
        canteens = crud.get_all_canteens(db)
        return serialize_for_llm(canteens, user_lat, user_lon)

    if function == "get_restaurants":
        restaurants = crud.get_restaurants_by_canteen(db, canteen_id=args.get("canteen_id"))
        return serialize_for_llm(restaurants, user_lat, user_lon)

    raise ValueError(f"Unknown function: {function}")