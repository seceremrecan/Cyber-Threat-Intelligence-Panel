from src.api.alienvault import get_alienvault_data
from src.api.models.models import ApiIoC, DomainIoC
from database import create_specific_ioc_db
from src.api.ipgeolocation import get_ip_location
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from config import settings
import requests
import re

# Veritabanı bağlantısı
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

def is_email(ioc: str) -> bool:
    """
    Verilen IoC'nin e-mail olup olmadığını kontrol eder.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, ioc) is not None


def check_http_security(domain: str):
    """
    Check HTTP Security headers for a given domain.
    """
    try:
        # Add "http://" if not already present
        if not domain.startswith("http"):
            domain = f"http://{domain}"

        response = requests.get(domain, timeout=5)
        headers = response.headers

        # Security headers to check
        security_headers = {
            "Content Security Policy": "Content-Security-Policy" in headers,
            "Strict Transport Security": "Strict-Transport-Security" in headers,
            "X-Content-Type-Options": "X-Content-Type-Options" in headers,
            "X-Frame-Options": "X-Frame-Options" in headers,
            "X-XSS-Protection": "X-XSS-Protection" in headers,
        }

        return [
            {"policy": key, "status": "Yes" if value else "No"}
            for key, value in security_headers.items()
        ]

    except Exception as e:
        print(f"Error checking HTTP security: {e}")
        return [{"policy": key, "status": "No"} for key in [
            "Content Security Policy", 
            "Strict Transport Policy", 
            "X-Content-Type-Options", 
            "X-Frame-Options", 
            "X-XSS-Protection"
        ]]

    
def log_to_database(ioc, ip, ioc_type, geometric_location, city, country, is_valid, source, malicious):
    """
    IoC bilgilerini log_ioc tablosuna kaydetmek için kullanılan fonksiyon.
    """
    session = Session()
    try:
        existing_entry = session.query(ApiIoC).filter_by(ioc=ioc).first()
        if existing_entry:
            existing_entry.ip = ip
            existing_entry.ioc_type = ioc_type
            existing_entry.geometric_location = geometric_location
            existing_entry.city = city
            existing_entry.country = country
            existing_entry.is_valid = is_valid
            existing_entry.source = source
            existing_entry.malicious = malicious
            existing_entry.updated_time = datetime.utcnow()
            print(f"Updated IoC: {ioc}")
        else:
            new_entry = ApiIoC(
                ioc=ioc,
                ip=ip,
                ioc_type=ioc_type,
                geometric_location=geometric_location,
                city=city,
                country=country,
                is_valid=is_valid,
                source=source,
                malicious=malicious,
            )
            session.add(new_entry)
            print(f"Added new IoC: {ioc}")
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error logging IoC: {e}")
    finally:
        session.close()

def handle_domain(ioc: str):
    session = Session()
    ioc = ioc.strip().lower()
    print(f"Processing IoC: {ioc}")
    try:
        if is_email(ioc):
            ioc_type = "Email"
            email_query = session.execute(
                text("SELECT email, data_breach_id FROM emails WHERE TRIM(LOWER(email)) = TRIM(:email)"),
                {"email": ioc}
            ).fetchone()
            if email_query:
                email, data_breach_id = email_query
                breach_query = session.execute(
                    text("""
                        SELECT company_name, type, date_published, records_affected, description
                        FROM data_breach
                        WHERE id = :data_breach_id
                    """),
                    {"data_breach_id": data_breach_id}
                ).fetchone()
                if breach_query:
                    company_name, breach_type, date_published, records_affected, description = breach_query
                    log_to_database(
                        ioc=ioc,
                        ip="",
                        ioc_type=ioc_type,
                        geometric_location="",
                        city="",
                        country="",
                        is_valid="Valid",
                        source="Database",
                        malicious="",
                    )
                    return {
                        "status": "success",
                        "message": "Email IoC processed.",
                        "data": {
                            "IoC": ioc,
                            "Company_Name": company_name,
                            "Type": ioc_type,
                            "Breach_Type": breach_type,
                            "Date_Published": str(date_published),
                            "Records_Affected": records_affected,
                            "Description": description or "",
                            "Http_Security": [],
                        },
                    }
        else:
            alienvault_data = get_alienvault_data(ioc)
            ioc_type = alienvault_data.get("type", "Unknown")
            domain_entry = session.query(DomainIoC).filter_by(address=ioc).first()
            if domain_entry:
                source = domain_entry.source
                is_valid = "Valid" if domain_entry.is_valid else "Invalid"
                malicious = domain_entry.malicious
                address_type = domain_entry.address_type
            else:
                source = ""
                is_valid = ""
                malicious = ""
                address_type = ioc_type

            http_security = check_http_security(ioc)
            ip_data = get_ip_location(ioc)
            lat = ip_data.get("lat", "")
            lon = ip_data.get("lon", "")
            geometric_location = f"{lat}, {lon}" if lat and lon else ""
            city = ip_data.get("city", "")
            country = ip_data.get("country", "")
            ip = ip_data.get("query", "")

            # Log IoC to database
            log_to_database(
                ioc=ioc,
                ip=ip,
                ioc_type=ioc_type,
                geometric_location=geometric_location,
                city=city,
                country=country,
                is_valid=is_valid,
                source=source,
                malicious=malicious,
            )

            return {
                "status": "success",
                "message": "Domain or IP processed.",
                "data": {
                    "IoC": ioc,
                    "Type": ioc_type,
                    "IP": ip,
                    "Geometric_Location": geometric_location,
                    "City": city,
                    "Country": country,
                    "Source": source,
                    "Is_Valid": is_valid,
                    "Malicious": malicious,
                    "Http_Security": http_security,
                },
            }
    except Exception as e:
        import traceback
        print(f"Exception occurred: {str(e)}")
        traceback.print_exc()
        return {"status": "failed", "message": str(e)}
    finally:
        print("Closing database session.")
        session.close()
