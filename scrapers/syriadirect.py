import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS

def get_syriadirect_data(date):
    """"""

def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """"""

def get_article_text(article_link):
    """Concatenates all paragraph elements in article into a single string,
    returns it"""

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # Identifies paragraphs and creates empty variable for text content
    paragraphs = soup.find("div", class_="sd_article_body").find_all("p", recursive=False)
    text_content = ""

    # Iterates thru paragraph elements and concatenates all elements containing text
    for paragraph in paragraphs:
        elements = paragraph.find_all(True)
        for element in elements:
            text_content = text_content + element.text
        text_content = text_content + "\n\n"

    return text_content

def get_timestamp(date):
    """Takes date input and converts it to Unix timestamp

    NOTE: Assumes date is in ISO 8601 format.
    """

    curr_date = date.split("T")[0]

    return time.mktime(datetime.datetime.strptime(curr_date, "%Y-%m-%d").timetuple())
