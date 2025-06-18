from fastapi import Depends, APIRouter
from sqlmodel import Session, delete
from Models.db_models import *
from Requests.auth_requests import auth_handler
from db.db import get_session

delete_route = APIRouter(dependencies = [Depends(auth_handler.get_current_user)])

@delete_route.delete("/results/clean", status_code=200, operation_id="delete_incomplete_results")
def delete_incomplete(session: Session = Depends(get_session)):
    statement = (
        delete(Results)
        .where(
            (Results.raceId == None) |
            (Results.driverId == None) |
            (Results.constructorId == None) |
            (Results.number == None) |
            (Results.grid == None) |
            (Results.position == None) |
            (Results.positionText == None) |
            (Results.positionOrder == None) |
            (Results.points == None) |
            (Results.laps == None) |
            (Results.time == None) |
            (Results.milliseconds == None) |
            (Results.fastestLap == None) |
            (Results.rank == None) |
            (Results.fastestLapTime == None) |
            (Results.fastestLapSpeed == None) |
            (Results.statusId == None)
        )
    )

    result = session.exec(statement)
    session.commit()
    return {"deleted_rows": result.rowcount}   # returns number of deleted rows

@delete_route.delete("/drivers/clean", status_code=200, operation_id="delete_incomplete_drivers")
def clean_drivers(session: Session = Depends(get_session)):
    statement = delete(Drivers).where(Drivers.code == None)
    result = session.exec(statement)
    session.commit()
    return {"deleted_rows": result.rowcount}  # Number of deleted rows