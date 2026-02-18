from sqlalchemy.orm import Session
import crud

def execute_function(db: Session, function: str, args: dict):
    if function == "get_canteens":
        return crud.get_all_canteens(db)

    if function == "get_restaurants":
        return crud.get_restaurants_by_canteen(
            db,
            canteen_id=args["canteen_id"]
        )

    raise ValueError(f"Unknown function: {function}")