import api_handle as api
from database.database import Database as DB
from Logger.logger import Logger
import json
import time
import logo_handle as logo
import datetime

# set up databases and logger
warnings_db = DB("warnings")
warning_details_db = DB("warning_details")
status_db = DB("status")
logger = Logger("Data Handler")

def fetch() -> None:
    """
    Fetches all warnings from the API and saves them to the warnings database
    """
    database_warnings = warnings_db.get_keys()
    fetched_warnings = api.request_warnings()
    
    for warning in fetched_warnings:
        if warning["id"] not in database_warnings:
            warnings_db.set_value(warning["id"], warning)
            logger.log(f"Added warning '{warning['id']}' to database", 3)
            set_status(warning["id"], "new")
        else:
            logger.log(f"Warning '{warning['id']}' already in database, continuing", 0)

def fetch_details(warning_id: str) -> None:
    """
    Fetches the details of a warning from the API and saves them to the warning_details database
    """
    if warning_id not in warning_details_db.get_keys():
        warning_details_db.set_value(warning_id, api.request_warning_details(warning_id))

def get_new_warning_ids() -> list:
    """
    Gets all warning ids that are new, based on the status database
    """
    status = status_db.get_raw()
    new_warnings = []

    for warning_id in warnings_db.get_keys():
        if status[warning_id] == "new":
            new_warnings.append(warning_id) 
    return new_warnings

def set_status(warning_id: str, status: str) -> None:
    """
    Sets the status of a warning in the status database
    
    new: details not fetched, not posted to Discord
    unseen: details fetched, not posted to Discord
    rewritten: rewritten to Discord embed format, not posted to Discord
    seen: posted to Discord
    
    """
    possible_statuses = ["new", "unseen", "seen", "rewritten"]
    
    if status not in possible_statuses:
        raise ValueError(f"Status '{status}' not in possible statuses: {possible_statuses}")
    else:
        status_db.set_value(warning_id, status)
        logger.log(f"Set status of '{warning_id}' to '{status}'", 3)

def get_warning(warning_id: str) -> dict:
    """
    Gets a warning from the warnings database
    """
    return warnings_db.get_value(warning_id)

def get_warning_details(warning_id: str):
    """
    Gets the details of a warning from the warning_details database
    """
    return warning_details_db.get_value(warning_id)

def rewrite_format(warning_id: str) -> dict:
    """
    
    warning format:
    {
            "id": "mow.DE-NW-PB-SE093-20230910-93-000",
            "version": 5,
            "startDate": "2023-09-10T12:56:19+02:00",
            "severity": "Minor",
            "urgency": "Immediate",
            "type": "Alert",
            "i18nTitle": {
                "de": "Blaualgen im Lippesee - Lippesee"
            },
            "transKeys": {
                "event": "BBK-EVC-081"
            }
        }
    Args:
        warning_id (str): _description_

    Returns:
        dict: _description_
    """
    
    content = dict(get_warning_details(warning_id))
    
    logo_img = logo.get_logo(content["sender"])
    
    if logo_img == None:
        logo_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Zivilschutzzeichen.svg/256px-Zivilschutzzeichen.svg.png"
    else:
        logo_img = api.api_urls["logo_img"].format(filename=logo_img)
    
    
    embed = {
        "title": content["info"][0]["headline"],
        "description": content["info"][0]["description"].replace("<br/>", "\n"),
        "location": content["info"][0]["area"][0]["areaDesc"],
        "id": warning_id,
        "time": reformat_time(content["sent"]),
        "logo": logo_img,
        "author": logo.get_sender_name(content["sender"]),
    }
    logger.log(f"Rewrote warning '{warning_id}' to embed format", 3)
    return embed

def reformat_time(input_time: str) -> datetime.datetime:
    """
    Reformats the time from the API to a datetime object
    API: 2023-10-20T09:53:22+02:00
    """
    output_time = datetime.datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%S%z")
    return output_time

def call():
    # fetch warnings
    fetch()
    
    # get new warnings
    new_warnings = get_new_warning_ids()
    
    # fetch details for new warnings, set status to unseen
    for warning_id in new_warnings:
        fetch_details(warning_id)
        set_status(warning_id, "unseen")
    
    # line up warnings to post
    discord_warnings = []
    
    for warning_id in status_db.get_keys():
        if status_db.get_value(warning_id) == "unseen":
            discord_warnings.append(rewrite_format(warning_id))
    logger.log(f"Prepared {len(discord_warnings)} warnings to post", 3)
    return discord_warnings