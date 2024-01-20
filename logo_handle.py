import api_handle as api
import data_handle as data
from database.database import Database as DB
from Logger.logger import Logger
import os

WORKING_DIR = os.getcwd()
LOGO_DIR = os.path.join(WORKING_DIR, "logos")

# set up database and logger
logger = Logger("Logo Handler")
logo_db = DB("logos")


def fetch_logos():
    """
    Gets called once, at the start of the bot script.

    Example Logo Object:
    "CAP@biwapp.de": {
        "senderId": "CAP@biwapp.de",
        "name": "BIWAPP",
        "image": "CAP_at_biwapp.de.png",
        "orientation": "1",
        "lastModificationDate": 1674558776233
    }

    """
    logger.log("Fetching logos", 0)

    logo_list = api.request_logo_list()

    # clean up logo list
    logo_list = logo_list["logos"]
    logo_dict = {}

    # add logos to dictionary based on senderId
    for logo in logo_list:
        logo_dict[logo["senderId"]] = logo
        logger.log(f"Added logo '{logo['name']}' to database", 3)

    # save logo dictionary to database
    logo_db.set_raw(logo_dict)

    logger.log("Finished fetching logos", 3)


def get_logo(sender: str) -> str:
    try:
        logo = logo_db.get_value(sender)
        return logo["image"]
    except:
        return None


def get_sender_name(sender: str) -> str:
    try:
        logo = logo_db.get_value(sender)
        return logo["name"]
    except:
        return sender
