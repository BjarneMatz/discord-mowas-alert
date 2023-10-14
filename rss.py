from datetime import datetime

import feedparser

from database.database import Database as DB
from Logger.logger import Logger


# Connect to the database
db = DB("rss_feed")

# Create a logger object
logger = Logger("RSS Feed")

def get_latest_feed_entry(rss_url: str) -> dict:
    """
    The function `get_latest_feed_entry` takes an RSS URL as input and returns the latest feed entry as
    a dictionary.

    Args:
      rss_url (str): The `rss_url` parameter is a string that represents the URL of an RSS feed.

    Returns:
      a dictionary that represents the latest feed entry from the provided RSS URL.
    """
    logger.log(f"Fetching RSS feed from '{rss_url}'")
    feed_entry = feedparser.parse(rss_url).entries[0]
    
    return feed_entry


def rewrite_time_string(timestring: str) -> tuple:
    """
    The function `rewrite_time_string` takes a time string in the format '%a, %d %b %Y %H:%M:%S %z' and
    returns a tuple containing a new time string in the format '%d.%m.%Y - %H:%M:%S' and a datetime
    object.

    Args:
      timestring (str): The timestring parameter is a string representing a date and time in the format
    '%a, %d %b %Y %H:%M:%S %z'.

    Returns:
      The function `rewrite_time_string` returns a tuple containing two elements. The first element is a
    string `new_time_str`, which represents the input `timestring` in the format "dd.mm.YYYY -
    HH:MM:SS". The second element is a datetime object `dt_obj`, which represents the input `timestring`
    parsed according to the format '%a, %d %
    """
    dt_obj = datetime.strptime(timestring, "%a, %d %b %Y %H:%M:%S %z")
    new_time_str = dt_obj.strftime("%d.%m.%Y - %H:%M:%S")

    return new_time_str, dt_obj


def rewrite_format(feed_entry: dict) -> dict:
    """
    The function `rewrite_format` takes a dictionary `feed_entry` as input and returns a modified
    dictionary `announce` with specific keys and values extracted from `feed_entry`.

    Args:
      feed_entry (dict): The `feed_entry` parameter is a dictionary that represents a single entry in a
    feed. It contains information such as the title, summary, published time, and link of the entry.

    Returns:
      The function `rewrite_format` returns a dictionary named `announce`.
    """
    description = str(feed_entry["summary"])
    description_seperator = description.find("---")
    description = description[0:description_seperator]  # snip unwanted content
    # description = description.join(f"\n\n Link: {feed_entry['link']}") #too long

    time = feed_entry["published"]
    time, dt_obj = rewrite_time_string(time)

    announce = {
        "title": feed_entry["title"],
        "description": description,
        "time": time,
        "link": feed_entry["link"],
        "date_object": dt_obj,
    }
    return announce


def extract_author(entry: dict):
    """
    The function `extract_author` takes in a dictionary `entry` and returns an author dictionary with
    default values, but if the string "Bundesamt für Seeschifffahrt und Hydrographie" is found in the
    `summary` key of the `entry` dictionary, the author dictionary is updated with specific values.

    Args:
      entry (dict): The `entry` parameter is a dictionary that represents a news entry. It contains
    information about the news article, such as the title, summary, and publication date.

    Returns:
      a dictionary containing the name, url, and logo of the author.
    """
    author = {}
    if "Bundesamt für Seeschifffahrt und Hydrographie" in entry["summary"]:
        author["name"] = "Bundesamt für Seeschifffahrt und Hydrographie"
        author["logo"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/BSH-Logo.svg/512px-BSH-Logo.svg.png"
        author["url"] = "https://www.bsh.de/aktdat/wvd/sturm/"
    elif "DWD" in entry["summary"] or "Deutscher Wetterdienst" in entry["summary"]:
        author["name"] = "Deutscher Wetterdienst"
        author["logo"] = "https://www.dwd.de/DE/service/copyright/dwd-logo-png.png?__blob=publicationFile&v=4"
        author["url"] = "https://www.dwd.de/DE/Home/home_node.html"
    else:
        author["name"] = "Bundesamt für Bevölkerungsschutz und Katastrophenhilfe"
        author["logo"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Zivilschutzzeichen.svg/256px-Zivilschutzzeichen.svg.png"
        author["url"] = "https://www.bbk.bund.de/DE/Home/home_node.html"
    return author


def entry_is_new(entry: dict) -> bool:
    """
    The function `entry_is_new` checks if an entry is new by returning `True` for now.

    Args:
      entry (dict): A dictionary representing an entry in a database.

    Returns:
      a boolean value, either True or False.
    """
    if entry["id"] in db.get_keys():
        return False
    else:
        return True

def save_entry_to_database(entry: dict):
    """
    The function `save_entry_to_database` saves the entry to the database.

    Args:
      entry (dict): A dictionary representing an entry in a database.

    Returns:
      None
    """
 
    db.set_value(entry["id"], entry)
    logger.log(f"Saved entry with id {entry['id']} to database", 3)


def external_request(url: str):
    """
    The function `external_request` makes an external request to a given URL, retrieves the latest feed
    entry, checks if it is new, and returns the formatted entry and author if it is new, otherwise it
    returns empty dictionaries.

    Args:
      url (str): A string representing the URL of the external request.

    Returns:
      The function `external_request` is returning a tuple. The first element of the tuple is the result
    of calling the `rewrite_format` function on the latest feed entry, and the second element is the
    result of calling the `extract_author` function on the latest feed entry. If the latest feed entry
    is not new, then an empty dictionary is returned as the first element of the tuple, and another
    """

    entry = get_latest_feed_entry(url)
    if entry_is_new(entry):
        logger.log("Latest entry is new, working on returning...", 3)
        save_entry_to_database(entry)
        return rewrite_format(entry), extract_author(entry)
    else:
        logger.log("Latest entry is not new")
        return {}, {}

