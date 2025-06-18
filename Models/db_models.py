from sqlmodel import SQLModel, Field
from typing import Optional

class Circuits(SQLModel, table=True):
    circuitId: Optional[int] = Field(default=None, primary_key=True)
    circuitRef: Optional[str]
    name: Optional[str]
    location: Optional[str]
    country: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    alt: Optional[int]
    url: Optional[str]

class Races(SQLModel, table=True):
    raceId: Optional[int] = Field(default=None, primary_key=True)
    year: Optional[int]
    round: Optional[int]
    circuitId: Optional[int] = Field(default=None, foreign_key="circuits.circuitId")
    name: Optional[str]
    date: Optional[str]
    time: Optional[str]
    url: Optional[str]

class Drivers(SQLModel, table=True):
    driverId: Optional[int] = Field(default=None, primary_key=True)
    driverRef: Optional[str]
    number: Optional[int]
    code: Optional[str]
    forename: Optional[str]
    surname: Optional[str]
    dob: Optional[str]
    nationality: Optional[str]
    url: Optional[str]

class Constructors(SQLModel, table=True):
    constructorId: Optional[int] = Field(default=None, primary_key=True)
    constructorRef: Optional[str]
    name: Optional[str]
    nationality: Optional[str]
    url: Optional[str]

class Results(SQLModel, table=True):
    resultId: Optional[int] = Field(default=None, primary_key=True)
    raceId: Optional[int] = Field(default=None, foreign_key="races.raceId")
    driverId: Optional[int] = Field(default=None, foreign_key="drivers.driverId")
    constructorId: Optional[int] = Field(default=None, foreign_key="constructors.constructorId")
    number: Optional[int]
    grid: Optional[int]
    position: Optional[int]
    positionText: Optional[str]
    positionOrder: Optional[int]
    points: Optional[float]
    laps: Optional[int]
    time: Optional[str]
    milliseconds: Optional[int]
    fastestLap: Optional[int]
    rank: Optional[int]
    fastestLapTime: Optional[str]
    fastestLapSpeed: Optional[float]
    statusId: Optional[int]

class Pitstops(SQLModel, table=True):
    raceId: int = Field(foreign_key="races.raceId", primary_key=True)
    driverId: int = Field(foreign_key="drivers.driverId", primary_key=True)
    stop: int = Field(primary_key=True)
    lap: Optional[int]
    time: Optional[str]
    duration: Optional[float]
    milliseconds: Optional[int]

class Laptimes(SQLModel, table=True):
    raceId: int = Field(foreign_key="races.raceId", primary_key=True)
    driverId: int = Field(foreign_key="drivers.driverId", primary_key=True)
    lap: int = Field(primary_key=True)
    position: Optional[int]
    time: Optional[str]
    milliseconds: Optional[int]

class Qualifyings(SQLModel, table=True):
    qualifyId: Optional[int] = Field(default=None, primary_key=True)
    raceId: Optional[int] = Field(default=None, foreign_key="races.raceId")
    driverId: Optional[int] = Field(default=None, foreign_key="drivers.driverId")
    constructorId: Optional[int] = Field(default=None, foreign_key="constructors.constructorId")
    number: Optional[int]
    position: Optional[int]
    q1: Optional[str]
    q2: Optional[str]
    q3: Optional[str]

class ConstructorStandings(SQLModel, table=True):
    constructorStandingsId: Optional[int] = Field(default=None, primary_key=True)
    raceId: Optional[int] = Field(default=None, foreign_key="races.raceId")
    constructorId: Optional[int] = Field(default=None, foreign_key="constructors.constructorId")
    points: Optional[float]
    position: Optional[int]
    positionText: Optional[str]
    wins: Optional[int]

class DriverStandings(SQLModel, table=True):
    driverStandingsId: Optional[int] = Field(default=None, primary_key=True)
    raceId: Optional[int] = Field(default=None, foreign_key="races.raceId")
    driverId: Optional[int] = Field(default=None, foreign_key="drivers.driverId")
    points: Optional[float]
    position: Optional[int]
    positionText: Optional[str]
    wins: Optional[int]

class ConstructorResults(SQLModel, table=True):
    constructorResultsId: Optional[int] = Field(default=None, primary_key=True)
    raceId: Optional[int] = Field(default=None, foreign_key="races.raceId")
    constructorId: Optional[int] = Field(default=None, foreign_key="constructors.constructorId")
    points: Optional[float]
    status: Optional[str]

class Status(SQLModel, table=True):
    statusId: Optional[int] = Field(default=None, primary_key=True)
    status: Optional[str]

class Seasons(SQLModel, table=True):
    year: int = Field(primary_key=True)
    url: Optional[str]