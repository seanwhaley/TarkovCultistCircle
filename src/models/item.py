from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    basePrice = Column(Float)
    lastLowPrice = Column(Float)
    avg24hPrice = Column(Float)
    updated = Column(String)

    def __repr__(self):
        return f"<Item(name={self.name}, basePrice={self.basePrice})>"
