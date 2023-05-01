from config.database import Base
from sqlalchemy import Column, Integer, String

class Clientes(Base):
    
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    sector = Column(String)
    metodologia = Column(Integer)
    pais = Column(String)
    