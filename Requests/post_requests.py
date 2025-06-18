from sqlmodel import Session
from Models.db_models import *
from Models.input_models import SeasonCreate
from fastapi import HTTPException, Depends, APIRouter

from Requests.auth_requests import auth_handler
from db.db import load_csvs_data, get_session

DATA_FOLDER = "data"  # Folder where CSV files are stored

post_route = APIRouter()

@post_route.post("/load-csv/")
def load_all_csvs():
    return load_csvs_data()

@post_route.post("/seasons/add", status_code=201)
def add_season(
    season_data: SeasonCreate,
    session: Session = Depends(get_session)) -> Seasons:
    existing = session.get(Seasons, season_data.year)
    if existing:
        raise HTTPException(status_code=400, detail="Season already exists")

    season = Seasons(**season_data.dict())
    session.add(season)
    session.commit()
    session.refresh(season)
    return season