import requests

import time
import datetime

from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS

class Base_Scraper:
    def __init__(self, url):
        self.url = url,
        self.article_list = []

    def scrape_data(self, stop_timestamp):
        """Scrapes data from a provided webpage up to a given time limit"""
        self.get_data(stop_timestamp)

    def get_data(self):
        """Placeholder method overidden in subclass"""
        pass

    def get_soup(self, url, headers=DEFAULT_HEADERS):
        """Generates a response/gets soup from a given server using requests and
        default headers"""

        # bs4 setup
        response = requests.get(url, headers)
        soup = BeautifulSoup(response.content, "html.parser")

        return soup
