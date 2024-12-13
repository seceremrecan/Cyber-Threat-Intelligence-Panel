from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ApiIoC(Base):
    __tablename__ = "log_ioc"

    ioc = Column(String, primary_key=True)
    ip = Column(String)
    ioc_type = Column(String)
    geometric_location = Column(String)
    city = Column(String)
    country = Column(String)
    created_time = Column(DateTime, default=func.now())  # Kayıt oluşturulma zamanı
    updated_time = Column(DateTime, onupdate=func.now())
    is_valid = Column(String)
    source = Column(String, nullable=False)
    malicious = Column(String, nullable=False)


class DomainIoC(Base):
    __tablename__ = "all_iocs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False, unique=True)  # Domain veya IP adresi
    address_type = Column(String, nullable=False)  # Adres tipi (Domain/IP)
    created_time = Column(DateTime, default=func.now())  # Kayıt oluşturulma zamanı
    updated_time = Column(DateTime, onupdate=func.now())  # Kayıt güncellenme zamanı
    source = Column(String, nullable=False)  # Kaynak (ör. USOM, PhishTank)
    malicious = Column(String, nullable=False)  # Kötücül davranış türü (ör. malware, phishing)
    is_valid = Column(String)  # Geçerlilik durumu (true/false)


class DataBreach(Base):
    """
    Veri ihlali bilgilerini tutar.
    """
    __tablename__ = "data_breach"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, nullable=False)  # İhlale uğrayan şirket adı
    type = Column(String, nullable=False)  # İhlal türü (ör. şifre, kredi kartı bilgileri)
    records_affected = Column(Integer)
    date_published = Column(DateTime, nullable=False)  # İhlalin yayınlanma tarihi
    description = Column(String)  # İhlalle ilgili açıklama
    emails = relationship("Email", back_populates="data_breach")  # İlişkilendirilmiş e-postalar
    created_at = Column(DateTime, default=func.now())  # Kayıt oluşturulma zamanı
    updated_at = Column(DateTime, onupdate=func.now())  # Kayıt güncellenme zamanı


class Email(Base):
    """
    E-posta adreslerini tutar ve veri ihlalleriyle ilişkilendirir.
    """
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)  # E-posta adresi
    data_breach_id = Column(Integer, ForeignKey("data_breach.id"))  # İlgili data breach ID
    data_breach = relationship("DataBreach", back_populates="emails")  # Data breach ile ilişki
    created_at = Column(DateTime, default=func.now())  # Kayıt oluşturulma zamanı
    updated_at = Column(DateTime, onupdate=func.now())  # Kayıt güncellenme zamanı

# Not: `IpIoC` sınıfı kullanımdan kaldırılmış veya gerekliyse yeniden düzenlenebilir.
