import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_LATIN_MONTHS

def get_hfl_data(date):
    """"""

def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of HFL articles until time limit reached.
    TODO: Handle server timeout while looping
    """

    #bs4 setup
    response = requests.get(
        f"https://www.horanfree.com/page/{page_num}?cat=%2A"
    )
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("li", class_="post-item")

    # List of articles to be returned
    article_list = []

    count = 1

    # Gathers article info for each post on single page
    for a in articles:
        # identifies date posted and generates Unix timestamp
        date_posted = a.find("span", class_="date meta-item tie-icon").text
        current_timestamp = get_timestamp(date_posted)
        link = a.find("a", class_=None).get("href")

        # Verifies that current_timestamp is less than (earlier than) limit,
        # breaks loop if so.
        if stop_timestamp and current_timestamp < stop_timestamp:
            break

        # Gets title and basic data and creates dict for article
        article = {
            "title": a.find("h2", class_="post-title").text,
            "date_posted": current_timestamp,
            "link": link,
            "full_text": get_article_text(link)
        }

        print(count)
        count += 1
        article_list.append(article)

    # Recursively call function for next page until stop_timestamp is reached
    if stop_timestamp and current_timestamp >= stop_timestamp:
        next_page_num = page_num + 1
        article_list += get_news_articles_by_page(
            page_num=next_page_num, stop_timestamp=stop_timestamp
        )

    return article_list


def get_article_text(article_link):
    """Gathers article text content from link to given article. Concatenates all
    paragraph elements into single string and returns it."""

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

