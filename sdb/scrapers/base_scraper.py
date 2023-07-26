import requests

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from sdb.scrapers.utils import DEFAULT_HEADERS, ScrapingError


class BaseScraper(ABC):
    """This is the default class for each web scraper. It contains base functionality
    used regularly by each scraper and allows for logic to be centralized and
    easily changed.
    """

    def get_data(self, stop_timestamp):
        """Default method for initializing scraper. Can be called on any instanced
        subclass with a timetsamp and will return scraped data up until said
        timestamp.
        """
        scraped_articles = self.get_news_articles_by_page(stop_timestamp=stop_timestamp)

        return scraped_articles

    @abstractmethod
    def get_news_articles_by_page(self):
        """Placeholder method overidden in subclasses where articles are gathered
        through pagination.
        """
        pass

    def get_soup(self, url):
        """Generates a response/gets soup from a given server using requests and
        default headers
        TODO: Add logic to handle server timeouts here.
        """

        # bs4 setup: Attempts get request from server and prints error message
        # if any error occurs.


        # NOTE: This will raise a scraping error BUT it will retain the original
        # exception in the __cause__ atribute of the ScrapingError object. The
        # "from e" is a neat little trick to ease debugging a bit.
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        except Exception as e:
            raise ScrapingError(f"Failed to get response from {url}", url) from e

        soup = BeautifulSoup(response.content, "html.parser")

        return soup

    def entry_added_message(self, count=1, page_num=1):
        """Prints a terminal message to the user when a new entry is added."""

        print(f"Added {count} entries from page {page_num}")

    def next_page_message(self, count=1, page_num=1):
        """Prints a terminal message when the page number increments during
        scraping
        """

        print(f"Continuing to page {page_num}")

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
    def should_continue_pagination(stop_timestamp=False, current_timestamp=False):
        """Returns true if current timestamp hasn't reached limit, else returns
        false. Used in logic determining whether to continue pagination while
        scraping.
        """

        if stop_timestamp and current_timestamp >= stop_timestamp:
            return True

        return False
