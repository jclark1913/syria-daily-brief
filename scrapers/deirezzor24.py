import requests

import time
import datetime
import math

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_TIME_UNITS


def get_deirezzor24_data(stop_timestamp):
    """Scrapes DEZ24 and collects all articles until the timestamp is reached.
    Returns all data as a dictionary.
    """

    scraped_articles = get_news_articles_by_page(stop_timestamp=stop_timestamp)

    return scraped_articles


def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of DEZ24 articles until time limit is reached.
    TODO: Handle server timeout while looping
    """

    # bs4 setup
    response = requests.get(
        f"https://deirezzor24.net/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1/page/{page_num}/"
    )
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find("div", class_="vce-loop-wrap").find_all("article")

    # List of articles to be returned
    article_list = []

    count = 1

    # Gathers article info for each post on single page

    for a in articles:
        # Get article link
        content = a.find("h2", class_="entry-title")
        link = content.find("a").get("href")

        # Destructure last_updated and article_text
        [last_updated, article_text] = list(
            get_article_text_and_last_updated(link).values()
        )

        # Get current timestamp for article
        current_timestamp = get_approx_timestamp_from_last_updated(last_updated)

        # Verifies that current_timestamp is less than (earlier than) limit,
        # breaks loop if so.
        if stop_timestamp and current_timestamp < stop_timestamp:
            break

        article = {
            "title": content.text,
            "date_posted": current_timestamp,
            "link": link,
            "full_text": article_text,
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


def get_article_text_and_last_updated(article_link):
    """Gets the text from a single article as well as the description in Arabic
    explaining how recently the article was published.
    """

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # Identifies paragraphs and creates empty variable for text content
    paragraphs = soup.find("div", class_="entry-content").find_all("p", recursive=False)
    article_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

    # Get last_updated to generate timestamp
    last_updated = soup.find("span", class_="updated").text

    return {"last_updated": last_updated, "article_text": article_text}


def get_approx_timestamp_from_last_updated(last_updated):
    """Converts Arabic phrase in description to approximate timestamp.

    Assuming current time is 6/20/23 9pm (1687309200):

    "5 ساعات ago" -> (1687291200)
    """

    # get current date
    current_timestamp = math.floor(datetime.datetime.now().timestamp())

    # subtract total seconds from desc from current date to generate approx timestamp
    return current_timestamp - get_total_seconds_from_last_updated(last_updated)


def get_total_seconds_from_last_updated(last_updated):
    """Returns the total number of seconds from the posted before section of an
    article. Useful for generating a unix timestamp by subtracting result from
    current time.

    examples:

    "5 ساعات ago" -> 18000 (3600 * 5)
    "8 سنوات ago" -> 252455408 (63113852 * 8)
    "دقيقتين ago" -> 120 (60 * 2)

    """

    # Return variable
    total_seconds = 0

    # Create array of Arabic unit + quantity (if present)
    arabic_posted = [word for word in last_updated.split() if word != "ago"]

    # The word for "one" in Arabic (minus gender ending)
    arabic_one = "واحد"

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
