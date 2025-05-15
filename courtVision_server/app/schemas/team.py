from pydantic import BaseModel

class TeamBase(BaseModel):
    name: str
    abbreviation: str
    city: str
    state: str
    conference: str
    division: str
    founded: int
    logo: str | None = None

class TeamCreate(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int

    class Config:
        orm_mode = True
