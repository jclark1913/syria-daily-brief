import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_LATIN_MONTHS

def get_sdfpress_data(date):
    """"""

def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """"""

def get_article_text(article_link):
    """"""

def get_timestamp(date):
    """Converts Arabic date in 'YYYY, dd month' format to unix timestamp"""

    # Get number of Arabic month and replace it in string
    for month in ARABIC_LATIN_MONTHS:
        if month in date:
            translated_date = date.replace(month, ARABIC_LATIN_MONTHS[month])

    return time.mktime(datetime.datetime.strptime(translated_date, "%m %d, %Y").timetuple())








