from src.api.alienvault import get_alienvault_data
from src.api.models.models import ApiIoC, DomainIoC
from database import create_specific_ioc_db
from src.api.ipgeolocation import get_ip_location
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import settings

# Veritabanı bağlantısı
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

def handle_domain(ioc: str):
    """
    Bir IoC'yi işler:
    1. `domain_ioc` tablosundan source, category, is_valid bilgilerini kontrol eder.
    2. AlienVault API'den verileri alır ve `ApiIoC` tablosuna kaydeder.
    """
    session = Session()
    print(f"Processing IoC: {ioc}")  # IoC başlangıcı
    try:
        # domain_ioc tablosundan verileri kontrol et
        domain_entry = session.query(DomainIoC).filter_by(domain_address=ioc).first()
        print(f"Domain Entry from Database: {domain_entry}")  # Tablodan alınan giriş
        
        if domain_entry:
            print(f"Source: {domain_entry.source}, Category: {domain_entry.category}, Is Valid: {domain_entry.is_valid}")
            source = domain_entry.source
            category = domain_entry.category
            is_valid = "Yes" if domain_entry.is_valid else "No"
        else:
            print("Domain not found in database.")  # Eğer giriş bulunmazsa
            source = "Unknown"
            category = "Unknown"
            is_valid = "Unknown"
        
        print(f"Resolved Values - Source: {source}, Category: {category}, Is Valid: {is_valid}")  # Çözülmüş değerler
        
        # AlienVault API'den verileri al
        print("Fetching data from AlienVault API...")  # AlienVault API çağrısı
        alienvault_data = get_alienvault_data(ioc)
        print(f"AlienVault API Data: {alienvault_data}")  # API'den dönen veri
        
        if not alienvault_data:
            return {
                "status": "failed",
                "message": "No data from AlienVault or domain not found in database.",
            }

        # AlienVault verilerini işle
        ioc_type = alienvault_data.get("type", "Unknown")
        print(f"IoC Type: {ioc_type}")  # IoC türü
        ip_data = get_ip_location(ioc)
        print(f"IP Data: {ip_data}")  # IP konum verisi
        
        lat = ip_data.get("lat", "Unknown")
        lon = ip_data.get("lon", "Unknown")
        geometric_location = (
            f"{lat}, {lon}" if lat != "Unknown" and lon != "Unknown" else "Unknown"
        )
        city = ip_data.get("city", "Unknown")
        country = ip_data.get("country", "Unknown")
        ip = ip_data.get("query", "Unknown")
        
        print(f"Location Data - Lat: {lat}, Lon: {lon}, City: {city}, Country: {country}")  # Konum bilgisi

        # ApiIoC kaydı oluştur
        api_ioc = ApiIoC(
            ioc=ioc,
            ioc_type=ioc_type,
            ip=ip,
            geometric_location=geometric_location,
            city=city,
            country=country,
        )
        print(f"ApiIoC to Save: {api_ioc}")  # Kaydedilecek API IoC bilgisi

        # Veritabanına kaydet (create_specific_ioc_db ile)
        print("Saving ApiIoC to database...")
        status = create_specific_ioc_db(api_ioc, ApiIoC)
        if not status:
            print("Failed to save ApiIoC to database.")
            return {"status": "failed", "message": "Failed to save to database"}
        
        print("ApiIoC successfully saved to database.")  # Başarıyla kaydedildi
        
        # Tüm bilgileri döndür
        result = {
            "status": "success",
            "message": "Domain information successfully saved and retrieved.",
            "data": {
                "IoC": ioc,
                "Type": ioc_type,
                "IP": ip,
                "Geometric_Location": geometric_location,
                "City": city,
                "Country": country,
                "Source": source,
                "Category": category,
                "Is_Valid": is_valid,
            },
        }
        print(f"Returning Result: {result}")  # Dönen sonuç
        return result

    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # Hata ayıklama
        return {"status": "failed", "message": str(e)}
    finally:
        print("Closing database session.")  # Oturum kapanışı
        session.close()
