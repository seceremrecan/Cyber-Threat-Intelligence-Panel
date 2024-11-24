import httpx
import logging


def get_ip_location(ioc):
    """
    IP bilgilerini almak için senkron bir fonksiyon.
    """
    url = f"http://ip-api.com/json/{ioc}"
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            return data
    except Exception as e:
        logging.error(f"Failed to get IP location data for {ioc}. Error: {str(e)}")
        return {}
