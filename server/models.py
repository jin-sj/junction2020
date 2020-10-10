from sqlalchemy import Column, Integer, String, Float

from database import Base

class NamedEntity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    score = Column(Float)
    entity = Column(String)
