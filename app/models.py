from sqlalchemy import Column, String, Numeric, Integer
from database import Base

class Video(Base):

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True) 
    price = Column(Numeric(10,2))