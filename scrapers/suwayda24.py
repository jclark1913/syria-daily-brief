import requests

import time
import datetime
import math

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_TIME_UNITS, get_generic_timestamp

def get_suwayda24_data(date):
    """"""

def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """"""

def get_article_text(article_link):
    """"""

def get_approx_timestamp_from_last_updated(last_updated):
    """"""

def get_total_seconds_from_last_updated(last_updated):
    """"""

    # Return variable
    total_seconds = 0

    # Create array of Arabic unit + quantity (if present)
    arabic_posted = [word for word in last_updated.split() if word != "مضت"]

    # The word for "one" in Arabic (minus gender ending)
    arabic_one = "واحد"

    print(arabic_posted)

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

    # Generate # of seconds from Arabic time units dictionary
    for unit in ARABIC_TIME_UNITS:
        if duration in ARABIC_TIME_UNITS[unit]["arabic"]:
            total_seconds = ARABIC_TIME_UNITS[unit]["value"] * quantity

    return total_seconds