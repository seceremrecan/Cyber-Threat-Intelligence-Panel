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

    

def handle_domain(ioc: str):
    session = Session()
    ioc = ioc.strip().lower()  # Leading veya trailing boşlukları temizle ve küçük harfe çevir

    print(f"Processing IoC: {ioc}")
    try:
        if is_email(ioc):  # IoC'nin e-posta olup olmadığını kontrol et
            ioc_type = "Email"
            print(f"Querying email: {ioc}")

            # Emails tablosunda e-posta sorgula
            email_query = session.execute(
                text("SELECT email, data_breach_id FROM emails WHERE TRIM(LOWER(email)) = TRIM(:email)"),
                {"email": ioc}
            ).fetchone()

            print(f"Email Query Result: {email_query}")  # Debug için sonucu yazdır

            if email_query:
                # `data_breach_id` değerini al
                email, data_breach_id = email_query  # Tuple unpacking
                print(f"Email found: {email}, Data Breach ID: {data_breach_id}")

                # `data_breach_id` ile data_breach tablosunda veri sorgula
                breach_query = session.execute(
                    text("""
                        SELECT company_name, type, date_published, records_affected, description
                        FROM data_breach
                        WHERE id = :data_breach_id
                    """),
                    {"data_breach_id": data_breach_id}
                ).fetchone()

                print(f"Data Breach Query Result: {breach_query}")  # Debug için sonucu yazdır

                if breach_query:
                    # Tuple unpacking kullanarak alanlara erişim
                    company_name, breach_type, date_published, records_affected, description = breach_query

                    print(f"Data Breach Found: {company_name}")
                    

                    # Data breach verilerini döndür
                    return {
                        "status": "success",
                        "message": "Email IoC processed.",
                        "data": {
                            "IoC": ioc,
                            "Company_Name": company_name,
                            "Type": ioc_type,
                            "Breach_Type":breach_type,
                            "Date_Published": str(date_published),
                            "Records_Affected": records_affected,
                            "Description": description or "",
                            "Http_Security": [],  # No HTTP Security for email
                        },
                    }
                    
                else:
                    print("No matching data breach found.")
                    return {
                        "status": "success",
                        "message": "Email IoC processed, no data breach information found.",
                        "data": {
                            "IoC": ioc,
                            "Type": ioc_type,
                            "Http_Security": [],
                        },
                    }
            else:
                print(f"Email '{ioc}' not found in the emails table.")
                return {
                    "status": "failed",
                    "message": f"Email '{ioc}' not found in the database.",
                }

        else:
            # AlienVault API kullanarak IoC türünü belirle
            alienvault_data = get_alienvault_data(ioc)
            ioc_type = alienvault_data.get("type", "Unknown")
            print(f"AlienVault detected type: {ioc_type}")

            # Domain veya IP kontrolü
            domain_entry = session.query(DomainIoC).filter_by(address=ioc).first()
            print(f"Domain Entry from Database: {domain_entry}")

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

            print(f"Resolved Values - Source: {source}, Is Valid: {is_valid}")
            http_security = check_http_security(ioc)
            if not alienvault_data or not alienvault_data.get("data"):
                return {
                    "status": "failed",
                    "message": f"No data found for '{ioc}' in AlienVault or database.",
                }

            ip_data = get_ip_location(ioc)
            lat = ip_data.get("lat", "")
            lon = ip_data.get("lon", "")
            geometric_location = f"{lat}, {lon}" if lat and lon else ""
            city = ip_data.get("city", "")
            country = ip_data.get("country", "")
            ip = ip_data.get("query", "")

            print(f"Location Data - Lat: {lat}, Lon: {lon}, City: {city}, Country: {country}")

            # Döndürülecek sonuç
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
                    "Address_Type": address_type,
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

