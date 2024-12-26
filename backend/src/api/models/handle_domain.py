from src.api.alienvault import get_alienvault_data
from src.api.models.models import ApiIoC, DomainIoC
from database import create_specific_ioc_db
from src.api.ipgeolocation import get_ip_location
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from config import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import requests
import httpx
import logging
from config import settings
import re

# Veritabanı bağlantısı
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)


def is_email(ioc: str) -> bool:
    """
    Verilen IoC'nin e-mail olup olmadığını kontrol eder.
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
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
        return [
            {"policy": key, "status": "No"}
            for key in [
                "Content Security Policy",
                "Strict Transport Policy",
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
            ]
        ]


def log_to_database(
    ioc, ip, ioc_type, geometric_location, city, country, is_valid, source, malicious
):
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


def get_website_status(domain: str):
    """
    Verilen bir domain için UP/DOWN durumunu ve "Last Down" bilgisini döner.
    """
    # Zaman damgası
    timestamp = int(time.time() * 1000)

    # Protokol kontrolü: Kullanıcı HTTPS veya HTTP belirtmemişse otomatik eklenir
    if not domain.startswith(("http://", "https://")):
        domain_https = f"https://{domain}"
        domain_http = f"http://{domain}"
    else:
        domain_https = domain if domain.startswith("https://") else None
        domain_http = domain if domain.startswith("http://") else None

    def try_request(url):
        """Belirtilen URL'yi kontrol eder ve sonuç döner."""
        try:
            response = requests.get(url, allow_redirects=True, timeout=10)
            redirected_url = response.url if response.url != url else None
            return {
                "status": "UP",
                "url": url,
                "redirectedURL": redirected_url or url,
                "statusCode": response.status_code,
                "reasonPhrase": response.reason,
            }
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.Timeout:
            return {"status": "DOWN", "url": url, "error": "Request timed out."}
        except Exception as e:
            return {"status": "DOWN", "url": url, "error": f"An error occurred: {str(e)}"}

    # HTTPS öncelikli kontrol
    result = None
    if domain_https:
        result = try_request(domain_https)
    # HTTPS başarısızsa HTTP kontrolü
    if not result and domain_http:
        result = try_request(domain_http)

    # Eğer UP durumu tespit edildiyse Last Down bilgisini eklemek için devam et
    last_down = "Unknown"
    if result and result["status"] == "UP":
        try:
            isitdown_url = f"https://www.isitdownrightnow.com/check.php?domain={domain}"
            isitdown_response = requests.get(isitdown_url, timeout=10)
            isitdown_response.raise_for_status()

            # HTML'yi parse et
            soup = BeautifulSoup(isitdown_response.text, "html.parser")

            # "Last Down" bilgisini bul
            all_divs = soup.find_all("div", class_="tabletrsimple")
            for div in all_divs:
                if div.find("b") and "Last Down:" in div.find("b").text:
                    last_down = div.find("span", class_="tab").text.strip()
                    break
        except Exception as e:
            print(f"[ERROR] 'Last Down' bilgisini alırken hata: {e}")

    # Sonuçları birleştir ve döndür
    if result:
        result["last_down"] = last_down
        result["timestamp"] = timestamp
        return result

    # Tüm denemeler başarısız olursa DOWN olarak döner
    return {
        "status": "DOWN",
        "url": domain,
        "last_down": last_down,
        "timestamp": timestamp,
        "error": "Failed to connect using HTTP or HTTPS.",
    }





def get_dns_records(domain: str):
    """
    Fetches DNS records for the given domain using the DNSDumpster API.
    """
    headers = {"X-API-Key": settings.DNSDUMPSTER_API_KEY}

    try:
        url = f"https://api.dnsdumpster.com/domain/{domain}"
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP hatalarını yakalar

        data = response.json()
        return data
    except httpx.RequestError as e:
        logging.error(f"Request error while fetching DNS records for {domain}: {e}")
        return {"error": f"Request error: {e}"}
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error while fetching DNS records for {domain}: {e}")
        return {"error": f"HTTP status error: {e.response.status_code}"}
    except Exception as e:
        logging.error(f"Unexpected error while fetching DNS records for {domain}: {e}")
        return {"error": str(e)}


def get_robots_disallows(domain: str):
    """
    Fetch the robots.txt file of the domain and extract all Disallow rules.
    """
    try:
        url = f"http://{domain}/robots.txt"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {"status": "error", "message": "Could not fetch robots.txt"}

        disallows = []
        for line in response.text.splitlines():
            if line.strip().lower().startswith("disallow"):
                parts = line.split(":")
                if len(parts) > 1:
                    disallows.append(parts[1].strip())

        return {"status": "success", "data": disallows}
    except Exception as e:
        return {"status": "error", "message": str(e)}



def get_whois_data(ioc: str):
    """
    WHOIS verilerini almak için kullanılan senkron fonksiyon.
    """
    url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={settings.WHOIS_API_KEY}&domainName={ioc}&outputFormat=JSON"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data  # WHOIS verilerini döndür
    except Exception as e:
        logging.error(f"Failed to get WHOIS data for {ioc}. Error: {str(e)}")
        return {}


def handle_domain(ioc: str):
    session = Session()
    ioc = ioc.strip().lower()
    print(f"Processing IoC: {ioc}")
    try:
        if is_email(ioc):
            ioc_type = "Email"
            email_query = session.execute(
                text(
                    "SELECT email, data_breach_id FROM emails WHERE TRIM(LOWER(email)) = TRIM(:email)"
                ),
                {"email": ioc},
            ).fetchone()
            if email_query:
                email, data_breach_id = email_query
                breach_query = session.execute(
                    text(
                        """
                        SELECT company_name, type, date_published, records_affected, description
                        FROM data_breach
                        WHERE id = :data_breach_id
                    """
                    ),
                    {"data_breach_id": data_breach_id},
                ).fetchone()
                if breach_query:
                    (
                        company_name,
                        breach_type,
                        date_published,
                        records_affected,
                        description,
                    ) = breach_query
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
            whois_data = get_whois_data(ioc)
            dns_records = get_dns_records(ioc)
            # print(f"[DEBUG] DNS Records: {dns_records}")
            # Fetch website status
            website_status = get_website_status(ioc)
            print(f"[DEBUG] Website Status: {website_status}")

            robots_data = get_robots_disallows(ioc)  # Fetch robots.txt disallows
            # print(f"[DEBUG] Robots.txt Data: {robots_data}")

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
                    "DNS_Records": dns_records,
                    "Website_Status": website_status,
                    "Robots_Disallows": robots_data.get("data", [])
                    if robots_data["status"] == "success"
                    else [],
                    "WHOIS_Data": whois_data,  # Include website status in the response
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
