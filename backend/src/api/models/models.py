from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ApiIoC(Base):
    __tablename__ = "api_ioc"

    ioc = Column(String, primary_key=True)
    ip = Column(String)
    ioc_type = Column(String)
    geometric_location = Column(String)
    city = Column(String)
    country = Column(String)


class DomainIoC(Base):
    __tablename__ = "domain_ioc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_address = Column(String, nullable=False, unique=True)  # Domain adresi
    created_time = Column(DateTime, default=func.now())  # Kayıt oluşturulma zamanı
    updated_time = Column(DateTime, onupdate=func.now())  # Kayıt güncellenme zamanı
    source = Column(String, nullable=False)  # Kaynak (ör. USOM, PhishTank)
    category = Column(String, nullable=False)  # Kategori (ör. phishing, malicious, blacklist)
    is_valid = Column(Boolean, default=True)  # Domain geçerliliği (true/false)


class IpIoC(Base):
    __tablename__ = "ip_ioc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String, nullable=False, unique=True)  # Domain adresi
    created_time = Column(DateTime, default=func.now())  # Kayıt oluşturulma zamanı
    updated_time = Column(DateTime, onupdate=func.now())  # Kayıt güncellenme zamanı
    source = Column(String, nullable=False)  # Kaynak (ör. USOM, PhishTank)
    category = Column(String, nullable=False)  # Kategori (ör. phishing, malicious, blacklist)
    is_valid = Column(Boolean, default=True)  # Domain geçerliliği (true/false)    
