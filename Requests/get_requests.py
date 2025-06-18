from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlmodel import Session, select, func
from typing import List
from sqlalchemy import cast, String

from Models.db_models import *
from Models.response_models import RacesPerYear, RaceResultShort, TopDriverPoints, FastestPitstop
from db.db import get_session, create_db_and_tables

get_route = APIRouter()

@get_route.get("/")
def read_root():
    create_db_and_tables()
    return {"status": "Tables created if they didn’t exist"}

@get_route.get("/drivers/", response_model=list[Drivers])
def read_drivers(session: Session = Depends(get_session)):
    statement = select(Drivers)
    results = session.exec(statement)
    return results

@get_route.get("/circuits/by-country/",  response_model=list[Circuits])
def read_circuits_by_country(
    country: str = Query(..., description="Country name to filter circuits by"),
    session: Session = Depends(get_session)):
    statement = select(Circuits).where(Circuits.country == country)
    results = session.exec(statement).all()
    return results

@get_route.get("/drivers/oldest", response_model=list[Drivers])
def read_oldest_drivers(
    session: Session = Depends(get_session),
    limit: int = Query(5, ge=1, le=100, description="Number of oldest drivers to return")):
    statement = (
        select(Drivers)
        .where(Drivers.dob != None)  # Exclude NULLs
        .order_by(Drivers.dob)
        .limit(limit))
    return session.exec(statement).all()

@get_route.get("/seasons/first", response_model=Seasons)
def read_first_season(session: Session = Depends(get_session)) -> Seasons | None:
    statement = select(Seasons).order_by(Seasons.year.asc()).limit(1)
    result = session.exec(statement).first()
    return result

@get_route.get("/races/by-year", response_model=list[RacesPerYear])
def read_races_per_year(session: Session = Depends(get_session)) -> List[RacesPerYear]:
    statement = (
        select(Races.year, func.count().label("total_races"))
        .group_by(Races.year)
        .order_by(Races.year))
    results = session.exec(statement).all()
    return [RacesPerYear(year=row[0], total_races=row[1]) for row in results]

@get_route.get("/races/results-by-year", response_model=list[RaceResultShort])
def read_race_results_by_year(
    year: int = Query(..., description="Year to filter race results by"),
    session: Session = Depends(get_session)) -> List[RaceResultShort]:
    statement = (
        select(
            Results.resultId,
            Results.raceId,
            Races.name,
            (Drivers.forename + " " + Drivers.surname).label("driver_name"),
            Constructors.name,
            Results.position,
            Results.points,
            Races.year)
        .join(Races, Races.raceId == Results.raceId)
        .join(Drivers, Drivers.driverId == Results.driverId)
        .join(Constructors, Constructors.constructorId == Results.constructorId)
        .where(Races.year == year)
        .order_by(Races.name, Results.position)
    )

    rows = session.exec(statement).all()
    return [
        RaceResultShort(
            resultId=row[0],
            raceId=row[1],
            race_name=row[2],
            driver_name=row[3],
            constructor_name=row[4],
            position=row[5],
            points=row[6],
            year=row[7]
        )
        for row in rows
    ]

@get_route.get("/drivers/top", response_model=list[TopDriverPoints])
def read_top_drivers(
    limit: int = Query(5, ge=1, le=100, description="Number of top drivers to return"),
    session: Session = Depends(get_session)) -> List[TopDriverPoints]:
    statement = (
        select(
            DriverStandings.driverId,
            (Drivers.forename + " " + Drivers.surname).label("driver_name"),
            Races.name,
            Races.year,
            DriverStandings.points)
        .join(Drivers, Drivers.driverId == DriverStandings.driverId)
        .join(Races, Races.raceId == DriverStandings.raceId)
        .order_by(DriverStandings.points.desc())
        .limit(limit)
    )

    rows = session.exec(statement).all()
    return [
        TopDriverPoints(
            driverId=row[0],
            driver_name=row[1],
            race_name=row[2],
            race_year=row[3],
            points=row[4]
        ) for row in rows
    ]

@get_route.get("/pitstops/fastest-by-year", response_model=list[FastestPitstop])
def read_fastest_pitstops(
    year: Optional[int] = Query(None, description="Year to filter by (optional)"),
    session: Session = Depends(get_session)) -> List[FastestPitstop]:
    # Base query for getting min duration

    if year:
        min_duration_query = (
            select(func.min(Pitstops.milliseconds))
            .join(Races, Races.raceId == Pitstops.raceId)
            .where(Races.year == year)  # or pass the year as a param
        )
    else:
        min_duration_query = select(func.min(Pitstops.milliseconds)).where(Pitstops.milliseconds.is_not(None))

    min_duration = session.exec(min_duration_query).one()

    # Main query for rows with matching duration
    statement = (
        select(
            (Drivers.forename + " " + Drivers.surname + " (" + func.ifnull(cast(Drivers.number, String), "?") + ")").label("driver_name"),
            Pitstops.lap,
            Pitstops.duration,
            Races.name,
            Races.year)
        .join(Drivers, Drivers.driverId == Pitstops.driverId)
        .join(Races, Races.raceId == Pitstops.raceId)
        .where(Pitstops.milliseconds == min_duration)
        .order_by(Races.year, Races.name))

    rows = session.exec(statement).all()

    return [
        FastestPitstop(
            driver_name=row[0],
            lap=row[1],
            duration=row[2],
            race_name=row[3],
            race_year=row[4]
        )
        for row in rows
    ]

