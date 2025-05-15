from pydantic import BaseModel

class SeasonBase(BaseModel):
    year: str

class SeasonCreate(SeasonBase):
    pass  # For creation you just need the year

class SeasonOut(SeasonBase):
    id: int

    class Config:
        orm_mode = True
