import requests

import time
import datetime
import math

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_TIME_UNITS


def get_deirezzor24_data(date):
    """Scrapes DEZ24 and collects all articles up to a given time limit. Returns
    all data as a dictionary.
    """


def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of DEZ24 articles until time limit is reached.
    TODO: Handle server timeout while looping
    """


def get_article_text_and_desc(article_link):
    """Gets the text from a single article as well as the description in Arabic
    explaining how recently the article was published.
    """

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # Identifies paragraphs and creates empty variable for text content
    paragraphs = soup.find("div", class_="entry-content").find_all("p", recursive=False)
    article_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

    # Get description to generate timestamp
    description = soup.find("span", class_="updated").text

    return {
        "last_updated": description,
        "article_text": article_text
            }

def get_approx_timestamp_from_last_updated(last_updated):
    """Converts Arabic phrase in description to approximate timestamp.

    Assuming current time is 6/20/23 9pm (1687309200):

    "5 ساعات ago" -> (1687291200)
    """

    # get current date
    current_timestamp = math.floor(datetime.datetime.now().timestamp())
    print("TIME NOW IS ", current_timestamp)

    # subtract total seconds from desc from current date to generate approx timestamp
    return current_timestamp - get_total_seconds_from_last_updated(last_updated)


def get_total_seconds_from_last_updated(last_updated):
    """Returns the total number of seconds from the posted before section of an
    article. Useful for generating a unix timestamp by subtracting result from
    current time.

    examples:

    "5 ساعات ago" -> 18000 (3600 * 5)
    "8 سنوات ago" -> 252455408 (63113852 * 8)
    "دقيقتين ago" -> 120 (60 * 2)

    """

    # Return variable
    total_seconds = 0

    # Create array of Arabic unit + quantity (if present)
    arabic_posted = [word for word in last_updated.split() if word != "ago"]

    # The word for "one" in Arabic (minus gender ending)
    arabic_one = "واحد"

    # Ascertains duration (Arabic) and number of units
    if len(arabic_posted) == 1:
        duration = arabic_posted[0]
        quantity = 2
    elif arabic_one in arabic_posted[1]:
        duration = arabic_posted[0]
        quantity = 1
    else:
        duration = arabic_posted[1]
        quantity = int(arabic_posted[0])

    print("Duration = ", duration)
    print("Quantity = ", quantity)

    # Generate # of seconds from Arabic time units dictionary
    for unit in ARABIC_TIME_UNITS:
        if duration in ARABIC_TIME_UNITS[unit]["arabic"]:
            total_seconds = ARABIC_TIME_UNITS[unit]["value"] * quantity

    return total_seconds
