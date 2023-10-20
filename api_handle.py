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
        return []

def request_warning_details(warning_id) -> dict:
    """Returns details for a warning"""
    request = requests.get(api_urls["details"].format(id=warning_id))
    if request.status_code == 200:
        logger.log(f"Fetched details for warning with id {warning_id}", 3)
        return dict(request.json())
    else:
        return {}
