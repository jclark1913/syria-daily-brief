import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS


def get_sana_data(stop_timestamp):
    """Scrapes sana.sy and collects all posts up to a given time limit. Returns
    all this data as dictionary.
    """

    scraped_articles = get_news_articles_by_page(stop_timestamp=stop_timestamp)

    return scraped_articles


def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of sana articles until time limit reached
    TODO: Handle server timeout while looping
    """

    # bs4 setup
    response = requests.get(
        f"https://sana.sy/?cat=29582&paged={page_num}", headers=DEFAULT_HEADERS
    )
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article", class_="item-list")

    # List of articles to be returned
    article_list = []

    count = 1
    # Gathers article info for each post on single page
    for a in articles:
        # identifies date posted and generates Unix timestamp
        date_posted = a.find("span", class_="tie-date").text
        current_timestamp = get_timestamp(date_posted)

        # Verifies that current_timestamp is less than (earlier than) limit,
        # breaks loop if so.
        if stop_timestamp and current_timestamp < stop_timestamp:
            break

        # Gets title from card + creates dict of basic data
        title = a.find("a", class_=None).text
        article = {
            "title": title,
            "date_posted": current_timestamp,
            "link": a.find("a", class_="more-link").get("href"),
        }

        print(count)
        count += 1
        # Adds dict attribute for article text then appends to article_list
        article["full_text"] = get_article_text(article["link"])
        article_list.append(article)

    # Recursively call function for next page until stop_timestamp is reached
    if stop_timestamp and current_timestamp >= stop_timestamp:
        next_page_num = page_num + 1
        article_list += get_news_articles_by_page(
            page_num=next_page_num, stop_timestamp=stop_timestamp
        )

    return article_list


def get_article_text(article_link):
    """Concatenates all paragraph elements in article into a single string and
    returns it"""

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # iterates thru paragraphs and concatenates text content
    paragraphs = soup.find("div", class_="entry").find_all("p", recursive=False)
    return "\n\n".join(paragraph.text for paragraph in paragraphs)


def get_timestamp(date):
    """Takes date input and converts it to Unix timestamp

    NOTE: Assumes date is in YYYY-mm-dd format.
    """

    # Uses time and datetime libs to generate Unix timestamp
    return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
