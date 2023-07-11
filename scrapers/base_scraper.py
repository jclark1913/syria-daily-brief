import requests

import time
import datetime
import math

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS, ARABIC_TIME_UNITS

class Base_Scraper:

    def get_data(self, stop_timestamp):
        """Placeholder method overidden in subclass"""
        scraped_articles = self.get_news_articles_by_page(stop_timestamp=stop_timestamp)

        return scraped_articles

    def get_news_articles_by_page(self):
        """Placeholder method overidden in subclass"""
        pass

    def get_soup(self, url):
        """Generates a response/gets soup from a given server using requests and
        default headers
        TODO: Add logic to handle server timeouts here.
        """

        # bs4 setup
        response = requests.get(url, headers=DEFAULT_HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")

        return soup


    # NOTE: These conditions are left in the base class to reduce repetition.
    # Should they change in the future I only need to update them here rather
    # than in each individual scraper.

    @staticmethod
    def reached_time_limit_loop(stop_timestamp=False, current_timestamp=False):
        """Returns true if current_timestamp is earlier than limit, else returns
        false. Called when iterating through articles in subclasses.
        """

        if stop_timestamp and current_timestamp < stop_timestamp:
            return True

        return False
    @staticmethod
    def reached_time_limit_recurse(stop_timestamp=False, current_timestamp=False):
        """Returns true if current timestamp hasn't reached limit, else returns
        false. Used in logic determining whether to recurse """

        if stop_timestamp and current_timestamp >= stop_timestamp:
            return True

        return False


    # NOTE: These time-related methods are stored as static methods in the hopes
    # that they can be updated and maintained to include more websites using a
    # similar format.
    @staticmethod
    def get_approx_timestamp_from_last_updated_AR(last_updated):
        """Converts Arabic phrase in description to approximate timestamp.

        Assuming current time is 6/20/23 9pm (1687309200):

        "5 ساعات ago" -> (1687291200)
        """

        # get current date
        current_timestamp = math.floor(datetime.datetime.now().timestamp())

        # subtract total seconds from desc from current date to generate approx timestamp
        return current_timestamp - Base_Scraper.get_total_seconds_from_last_updated_AR(last_updated)

    @staticmethod
    def get_total_seconds_from_last_updated_AR(last_updated):
        """Returns the total number of seconds from the posted before section of an
        article. Useful for generating a unix timestamp by subtracting result from
        current time.

        NOTE: Currently works with both Deir Ezzor 24 and Suwayda 24.

        examples:

        "5 ساعات ago" -> 18000 (3600 * 5)
        "8 سنوات ago" -> 252455408 (63113852 * 8)
        "دقيقتين ago" -> 120 (60 * 2)

        """

        # Return variable
        total_seconds = 0

        # Create array of Arabic unit + quantity (if present)
        arabic_posted = [word for word in last_updated.split() if word != "ago" and word != "منذ"]

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
