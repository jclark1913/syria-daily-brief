import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_LATIN_MONTHS


def get_enabbeladi_data(date):
    """Scrapes enabbeladi.net and collects all articles up to a given time limit.
    Returns all this data as a dictionary.

    NOTE: Dates currently must follow YYYY-mm-dd format.
    """

    lower_time_limit = get_timestamp_for_time_limit(date)

    scraped_articles = get_news_articles_by_page(stop_timestamp=lower_time_limit)

    return scraped_articles

    # Convert date to unix timestamp.


def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of Enab Beladi articles until time limit reached.
    TODO: Handle server timeout while looping

    NOTE: There is a peculiarity with Enab Beladi. The most recent 5-6 articles
    are "featured", and they don't have dates attached to their parent elements
    on page 1. I could circumvent this by getting their dates when I get the
    full text of the article, but for now I will assume that featured articles
    are from today (Enab Beladi is prolific and publishes 20+ articles each day)
    """

    # bs4 setup
    response = requests.get(
        f"https://www.enabbaladi.net/archives/category/online/page/{page_num}"
    )
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("div", class_="one-post")

    # List of articles to be returned
    article_list = []

    count = 1

    # Gathers article info for each post on single page

    for a in articles:
        content = a.find("div", class_="item-content")

        # The top featured articles do not have a timestamp on the main page, so
        # we assume that the top 5-6 featured articles are from today.
        if content.find("samp"):
            current_timestamp = get_arabic_timestamp(content.find("samp").text)
            date_posted = current_timestamp
        else:
            current_timestamp = int(time.time())
            date_posted = current_timestamp

        # Checks if current article is within lower time range
        if stop_timestamp and current_timestamp < stop_timestamp:
            break

        title = content.find("a").find("h3").text

        # Generates article object w/ date posted using datetime.fromtimestamp
        article = {
            "title": title,
            "date_posted": datetime.datetime.fromtimestamp(date_posted).strftime(
                "%d/%m/%Y"
            ),
            "link": a.find("a").get("href"),
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
    """Concatenates all paragraph elements in article into single string and
    returns it."""

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # Identifies paragraphs and creates empty variable for text content
    paragraphs = soup.find("div", class_="content-article").find_all(
        "p", recursive=False
    )
    return "\n\n".join(paragraph.text for paragraph in paragraphs)


def get_arabic_timestamp(date):
    """Converts Arabic date in 'YYYY, dd month' format to unix timestamp"""

    # Get number of Arabic month and replace it in string
    for month in ARABIC_LATIN_MONTHS:
        if month in date:
            translated_date = date.replace(month, ARABIC_LATIN_MONTHS[month])

    # Get unix timestamp from translated date
    return time.mktime(
        datetime.datetime.strptime(translated_date, "%m %d, %Y").timetuple()
    )


def get_timestamp_for_time_limit(date):
    """Takes date input and converts it to Unix timestamp

    NOTE: Assumes date is in YYYY-mm-dd format.
    """

    # Uses time and datetime libs to generate Unix timestamp
    return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
