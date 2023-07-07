import requests

import time
import datetime
import math
import unicodedata

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_TIME_UNITS, get_generic_timestamp


def get_suwayda24_data(date):
    """Scrapes Suwayda24 and collects all articles up to a given time limit. Returns
    all data as a dictionary.

    NOTE: Uses get_generic_timestamp given lack of actual dates on Suwayda24. Assumes
    date is in dd-mm-YYYY format for ease of use.
    """

    # Convert date to unix timestamp
    lower_time_limit = get_generic_timestamp(date)

    scraped_articles = get_news_articles_by_page(stop_timestamp=lower_time_limit)

    return scraped_articles



def get_news_articles_by_page(page_num=1, stop_timestamp=False):
    """Scrapes a single page of Suwayda24 articles until time limit is reached.
    TODO: Handle server timeout while looping
    """

    # bs4 setup
    response = requests.get(
        f"https://suwayda24.com/?cat=%2A&paged={page_num}", headers=DEFAULT_HEADERS
    )
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find("div", class_="post-listing archive-box").find_all("article")

    # List of articles to be returned
    article_list = []

    count = 1

    # Gathers article info for each post on a single page

    for a in articles:
        # Get article link
        content = a.find("h2", class_="post-box-title")
        link = content.find("a").get("href")
        last_updated = a.find("span", class_="tie-date").text
        print("FROM WEBPAGE: ", last_updated)

        # Get current timestamp for article
        if u"\u200f" in last_updated:
            current_timestamp = get_approx_timestamp_from_last_updated(last_updated)
        else:
            current_timestamp = get_s24_eng_timestamp(last_updated)

        # Verifies that current_timestamp is less than (earlier than) limit,
        # breaks loop if so.
        if stop_timestamp and current_timestamp < stop_timestamp:
            break

        article = {
            "title": content.text,
            "date_posted": current_timestamp,
            "link": link,
            "full_text": get_article_text(link),
        }

        print(count)
        count += 1
        article_list.append(article)
        if count > 10:
            break

    # Recursively call function for next page until stop_timestamp is reached
    if stop_timestamp and current_timestamp >= stop_timestamp:
        next_page_num = page_num + 1
        article_list += get_news_articles_by_page(
            page_num=next_page_num, stop_timestamp=stop_timestamp
        )

    return article_list


def get_article_text(article_link):
    """Returns text from a single article in Arabic"""

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # Identifies paragraphs and gathers text content from paragraphs
    paragraphs = soup.find("div", class_="entry").find_all("p", recursive=False)
    article_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

    return article_text


def get_approx_timestamp_from_last_updated(last_updated):
    """Converts Arabic phrase in description to approximate timestamp.

    Assuming current time is 6/20/23 9pm (1687309200):

    "5 ساعات مضت\n" -> (1687291200)
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

    "5 ساعات مضت \n" -> 18000 (3600 * 5)
    "8 سنوات مضت \n" -> 252455408 (63113852 * 8)
    "دقيقتين مضت \n" -> 120 (60 * 2)

    """

    # Return variable
    total_seconds = 0

    # Create array of Arabic unit + quantity (if present)
    arabic_posted = [sanitize_last_updated(word) for word in last_updated.split() if word != "مضت"]

    # The word for "one" in Arabic (minus gender ending)
    arabic_one = "واحد"

    print("IN HELPER FUNC: ", arabic_posted)

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


def sanitize_last_updated(last_updated):
    """Removes unicode 'RIGHT-TO-LEFT' character from a given string and returns
    it.
    """

    return last_updated.replace(u"\u200f", "")


def get_s24_eng_timestamp(last_updated):
    """Returns a unix timestamp for mm/dd/Y timestamps"""

    return time.mktime(datetime.datetime.strptime(last_updated, "%m/%d/%Y").timetuple())

