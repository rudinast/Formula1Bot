from pydantic import BaseModel

class SeasonCreate(BaseModel):
    year: int
    url: str