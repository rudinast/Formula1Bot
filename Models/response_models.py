from pydantic import BaseModel
from typing import Optional

class RacesPerYear(BaseModel):
    year: int
    total_races: int

class RaceResultShort(BaseModel):
    resultId: int
    raceId: int
    race_name: str
    driver_name: str
    constructor_name: str
    position: Optional[int]
    points: Optional[float]
    year: int

class TopDriverPoints(BaseModel):
    driverId: int
    driver_name: str
    race_name: str
    race_year: int
    points: float

class FastestPitstop(BaseModel):
    driver_name: str
    lap: int
    duration: float
    race_name: str
    race_year: int