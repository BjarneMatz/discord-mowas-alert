import json
import requests
from Logger.logger import Logger

logger = Logger("API Handler")

api_urls = {
    "all_warnings": "https://warnung.bund.de/api31/mowas/mapData.json",
    "details": "https://warnung.bund.de/api31/warnings/{id}.json",
    "logo_list": "https://warnung.bund.de/api31/appdata/gsb/logos/logos.json",
    "logo_img": "https://warnung.bund.de/api31/appdata/gsb/logos/{filename}"
}


def request_warnings() -> list:
    """Returns all warnings from MoWaS or None if request failed"""
    request = requests.get(api_urls["all_warnings"])
    if request.status_code == 200:
        logger.log("Fetched warnings from API", 3)
        return request.json()
    else:
        logger.log("Failed to fetch warnings from API", 2)
        return []


def request_warning_details(warning_id) -> dict:
    """Returns details for a warning"""
    request = requests.get(api_urls["details"].format(id=warning_id))
    if request.status_code == 200:
        logger.log(f"Fetched details for warning with id {warning_id}", 3)
        return dict(request.json())
    else:
        logger.log(f"Failed to fetch details for warning with id {warning_id}", 2)
        return {}


def request_logo_list() -> list:
    """Returns a list of all logos"""
    request = requests.get(api_urls["logo_list"])
    if request.status_code == 200:
        logger.log("Fetched logo list from API", 3)
        return request.json()
    else:
        logger.log("Failed to fetch logo list from API", 1)
        return []


def request_logo(filename: str) -> bytes:
    """Returns the logo with the given filename"""
    request = requests.get(api_urls["logo_img"].format(filename=filename))
    if request.status_code == 200:
        logger.log(f"Fetched logo '{filename}' from API", 3)
        return request.content
    else:
        logger.log(f"Failed to fetch logo '{filename}' from API", 1)
        return b''
