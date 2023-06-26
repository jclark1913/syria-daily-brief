import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS

def get_syriadirect_data(date):
    """Scrapes syriadirect.org and collects all articles up to a given time limit. Returns
    all of this data as an object.

    NOTE: Assumes that date is in YYYY-mm-dd format as used in Syria Direct timestamps. Will
    likely need to change in future once user can input custom dates.
    """

    # Convert input date to unix timestamp
    lower_time_limit = get_timestamp(date)

    scraped_articles = get_news_articles_by_page(stop_timestamp=lower_time_limit)

    return scraped_articles


def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of Syria Direct articles until time limit reached
    TODO: Handle server timeout while looping"""

    # bs4 setup
    response = requests.get(
        f"https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/{page_num}/?lang=ar"
        )
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find("div", class_="fusion-posts-container").find_all("article")

    # List of articles to be returned
    article_list = []

    count = 1

    # Gathers article info for each post on single page
    for a in articles:
        date_posted = a.find("span", class_="updated").text
        current_timestamp = get_timestamp(date_posted)

        # Verifies that current_timestamp is less than (earlier than) limit,
        # breaks loop if so.
        if stop_timestamp and current_timestamp < stop_timestamp:
            break

        title = a.find("h2").find("a").text
        article = {
            "title": title,
            "date_posted": date_posted,
            "link": a.find("h2").find("a").get("href")
        }

        print(count)
        count += 1

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
