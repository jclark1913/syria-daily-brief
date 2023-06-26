import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_LATIN_MONTHS

def get_enabbeladi_data(date):
    """Scrapes enabbeladi.net and collects all articles up to a given time limit.
    Returns all this data as a dictionary.

    TODO: NOTE: Dates
    """

    # Convert date to unix timestamp.


def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of Enab Beladi articles until time limit reached.
    TODO: Handle server timeout while looping
    """

def get_article_text(article_link):
    """Concatenates all paragraph elements in article into single string and
    returns it."""

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # TODO: add iteration

def get_timestamp(date):
    """Converts Arabic date in 'YYYY, dd month' format to unix timestamp"""

    # Get number of Arabic month and replace it in string
    for month in ARABIC_LATIN_MONTHS:
        if month in date:
            translated_date = date.replace(month, ARABIC_LATIN_MONTHS[month])

    # Get unix timestamp from translated date
    return time.mktime(datetime.datetime.strptime(translated_date, "%m %d, %Y").timetuple())


