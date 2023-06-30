import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS


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

def get_approx_timestamp_from_desc(desc):
    """Converts Arabic phrase in description to approximate timestamp.

    Assuming current time is 6/20/23 9pm (1687309200):

    "5 ساعات ago" -> (1687291200)

    """
