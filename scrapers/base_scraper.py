import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS

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
