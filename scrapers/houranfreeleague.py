import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_LATIN_MONTHS

def get_hfl_data(date):
    """"""

def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """"""

def get_article_text(article_link):
    """"""

    #bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # iterates thru paragraphs and concatenates text content
    paragraphs = soup.find(
        "div", class_="entry-content entry clearfix").find_all("p", recursive=False)
    return "\n\n".join(paragraph.text for paragraph in paragraphs)

def get_timestamp(date):
    """Converts Arabic date in 'dd, m, YYYY' format to unix timestamp"""

    # Get number of Arabic month and replace it in string
    for month in ARABIC_LATIN_MONTHS:
        if month in date:
            translated_date = date.replace(month, ARABIC_LATIN_MONTHS[month])

    # Get unix timestamp from translated date
    return time.mktime(datetime.datetime.strptime(translated_date, "%d %m، %Y").timetuple())

