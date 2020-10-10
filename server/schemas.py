from enum import Enum
from pydantic import BaseModel
from typing import List, Tuple


class Tweet(BaseModel):
    """Metaclass of a tweet. Used as input type checking for /ent POST method"""
    text: str

class NamedEntity(BaseModel):
    word: str
    score: float
    entity: str
    index: int

    class Config:
        orm_mode = True

class NamedEntityCreate(NamedEntity):
    pass

class NEROut(BaseModel):
    """Metaclass of response of recognized entities. Used as
    output type checking for /ent POST method"""
    entities: List[NamedEntity]

class FakeNewsOut(BaseModel):
    is_fake: bool

class SexismDetectionOut(BaseModel):
    is_fake: bool

class EntityTypeEnum(Enum):
    O = 0
    B_MISC = 1
    I_MISC = 2
    B_PER = 3
    I_PER = 4
    B_ORG = 5
    I_ORG = 6
    B_LOC = 7
    I_LOC = 8
