from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DomainIoC(Base):
    __tablename__ = "domain_ioc"

    ioc = Column(String, primary_key=True)
    ip = Column(String)
    ioc_type = Column(String)
    geometric_location = Column(String)
    city = Column(String)
    country = Column(String)
