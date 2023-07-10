import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS

class Base_Scraper:
    # def __init__(self, url_template):
    #     self.url_template = url_template,

    def scrape_data(self, stop_timestamp):
        """Scrapes data from a provided webpage up to a given time limit"""
        self.get_data(stop_timestamp)

    def get_data(self):
        """Placeholder method overidden in subclass"""
        pass

    def get_news_articles_by_page(self):
        """Placeholder method overidden in subclass"""
        pass

    def get_soup(self, url):
        """Generates a response/gets soup from a given server using requests and
        default headers"""

        # bs4 setup
        response = requests.get(url, headers=DEFAULT_HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")

        return soup


    # NOTE: These conditions are left in the base class to reduce repetition.
    # Should they change in the future I only need to update them here rather
    # than in each individual scraper.

    def reached_time_limit_loop(self, stop_timestamp=False, current_timestamp=False):
        """Returns true if current_timestamp is earlier than limit, else returns
        false. Called when iterating through articles in subclasses.
        """

        if stop_timestamp and current_timestamp < stop_timestamp:
            return True

        return False

    def reached_time_limit_recurse(self, stop_timestamp=False, current_timestamp=False):
        """Returns true if current timestamp hasn't reached limit, else returns
        false. Used in logic determining whether to recurse """

        if stop_timestamp and current_timestamp >= stop_timestamp:
            return True

        return False
