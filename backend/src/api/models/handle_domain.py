from src.api.alienvault import get_alienvault_data
from src.api.models.models import DomainIoC
from database import create_specific_ioc_db
from src.api.ipgeolocation import get_ip_location


def handle_domain(ioc: str):
    """
    Bir IoC'yi işler ve AlienVault'tan alınan verileri veritabanına kaydeder.
    """
    try:
        # AlienVault API'den verileri çek
        alienvault_data = get_alienvault_data(ioc)

        if not alienvault_data:
            return {"status": "failed", "message": "No data from AlienVault"}

        # Burada `alienvault_data` bir sözlük olduğu için .get() metodu kullanılabilir
        ioc_type = alienvault_data.get("type", "Unknown")
        ip_data = get_ip_location(ioc)
        lat = ip_data.get("lat", "Unknown")
        lon = ip_data.get("lon", "Unknown")
        geometric_location = (
            f"{lat}, {lon}" if lat != "Unknown" and lon != "Unknown" else "Unknown"
        )
        city = ip_data.get("city", "Unknown")
        country = ip_data.get("country", "Unknown")
        ip = ip_data.get("query", "Unknown")

        # DomainIoC modelini doldur
        domain_ioc = DomainIoC(
            ioc=ioc,
            ioc_type=ioc_type,
            ip=ip,
            geometric_location=geometric_location,
            city=city,
            country=country,
        )

        # Veritabanına kaydet
        status = create_specific_ioc_db(domain_ioc, DomainIoC)
        if not status:
            return {"status": "failed", "message": "Failed to save to database"}

        return {
            "status": "success",
            "message": "Domain information successfully saved.",
            "data": {
                "IoC": ioc,
                "Type": ioc_type,
                "IP": ip,
                "Geometric_Location": geometric_location,
                "City": city,
                "Country": country,
            },
        }

    except Exception as e:
        return {"status": "failed", "message": str(e)}
