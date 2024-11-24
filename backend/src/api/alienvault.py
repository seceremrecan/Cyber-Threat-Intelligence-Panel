import httpx
from urllib.parse import quote
import ipaddress
import logging
from config import settings  # .env dosyasından API anahtarını alır.


def get_alienvault_data(ioc: str):
    """
    AlienVault API'den IoC verilerini almak ve ek verilerle birlikte döndürmek için kullanılan fonksiyon.
    """
    headers = {"X-OTX-API-KEY": settings.OTX_API_KEY}

    try:
        # IoC'nin türünü belirle
        try:
            ipaddress.ip_address(ioc)
            is_ip = True
        except ValueError:
            is_ip = False

        if is_ip:  # IP adresi
            url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ioc}/general"
            ioc_type = "IPv4"
        elif "/" in ioc:  # URL
            quoted_ioc = quote(ioc, safe="")
            url = (
                f"https://otx.alienvault.com/api/v1/indicators/url/{quoted_ioc}/general"
            )
            ioc_type = "URL"
        elif "." in ioc:  # Domain
            url = f"https://otx.alienvault.com/api/v1/indicators/domain/{ioc}/general"
            ioc_type = "Domain"
        else:  # Hash
            url = f"https://otx.alienvault.com/api/v1/indicators/file/{ioc}/general"
            ioc_type = "hash"

        # API çağrısı
        response = httpx.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Pulse info verilerinden "tags" çıkart
        pulse_info = data.get("pulse_info", {})
        pulses = pulse_info.get("pulses", [])
        tags = set()
        for pulse in pulses:
            pulse_tags = pulse.get("tags", [])
            tags.update(pulse_tags)

        return {
            "data": data,  # Tüm dönen veriyi içerir
            "type": ioc_type,  # IoC türü
            "tags": list(tags),  # Pulse verilerinden çıkarılan tagler
        }

    except Exception as e:
        logging.error(f"Error fetching data from AlienVault for IoC: {ioc}. Error: {e}")
        return {
            "data": {},  # Boş veri döner
            "type": "unknown",  # Tür tanımlanamadıysa
            "tags": [],  # Hiçbir tag yok
        }
