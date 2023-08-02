from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from collections import namedtuple
import datetime
import requests

from sdb.scrapers.scraping_error import ScrapingError
from sdb.scrapers.scrape_result import ScrapeResult
from sdb.scrapers.utils import DEFAULT_HEADERS


ScraperConfig = namedtuple(
    "ScraperConfig",
    [
        "url_template",
        "publication",
        "should_get_metadata_during_pagination",
    ],
)


class BaseScraper(ABC):
    """This is the default class for each web scraper. It contains base functionality
    used regularly by each scraper and allows for logic to be centralized and
    easily changed.
    """

    def __init__(self):
        self.config = None  # Overridden in subclasses

    def get_data(self, stop_timestamp):
        """Default method for initializing scraper. Can be called on any instanced
        subclass with a timetsamp and will return scraped data up until said
        timestamp.
        """
        scraped_articles = self.get_news_articles_by_page(stop_timestamp=stop_timestamp)

        return scraped_articles

    def get_soup(self, url):
        """Generates a response/gets soup from a given server using requests and
        default headers. If an error occurs, a ScrapingError is raised.
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

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Placeholder method overidden in subclasses where articles are gathered
        through pagination.
        """

        # Dataclass scrape result to be returned
        scrape_result = ScrapeResult()
        url_template = self.config.url_template

        while True:
            # Generate correct url from template
            url = url_template.format(page_num=page_num)

            # bs4 setup
            try:
                soup = self.get_soup(url=url)
            except ScrapingError as e:
                print(f"Scraping error: {e}")
                scrape_result.success = False
                scrape_result.error_message = str(e)
                return scrape_result

            # Gets all articles on page
            articles = self.get_all_articles(soup)

            count = 1

            # Gathers article info for each post on single page
            for a in articles:
                # Gets article title
                title = self.get_article_title(a)
                link = self.get_article_link(a)

                if self.config.should_get_metadata_during_pagination:
                    date_posted = self.get_article_date_posted(a)
                    current_timestamp = self.get_timestamp(date_posted)
                    full_text = self.get_article_full_text(link)
                else:
                    [date_posted, full_text] = self.get_full_text_and_date_posted(
                        link
                    )
                    print("LAST UPDATED: ", date_posted)
                    current_timestamp = self.get_timestamp(date_posted)

                # Breaks loop if timestamp reached
                if self.reached_time_limit_loop(
                    stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
                ):
                    print("LOOP LIMIT REACHED")
                    return scrape_result

                article = {
                    "title": title,
                    "date_posted": current_timestamp,
                    "publication": self.config.publication,
                    "link": link,
                    "full_text": full_text,
                }

                # Send console message
                self.entry_added_message(count=count, page_num=page_num)
                print(current_timestamp)
                count += 1

                # Add article to scrape result
                scrape_result.article_list.append(article)

            # Checks if stop timestamp reached
            if not self.should_continue_pagination(
                stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
            ):
                print(
                    "PAGINATION LIMIT REACHED, STOP_TIMESTAMP= ",
                    stop_timestamp,
                    "CURRENT_TIMESTAMP= ",
                    current_timestamp,
                )
                return scrape_result

            # Go to next page
            page_num = page_num + 1

            # Send console message
            self.next_page_message(count=count, page_num=page_num)

    # NOTE: These methods are all overridden in subclasses.

    @abstractmethod
    def get_all_articles(self, soup):
        """Returns all articles on a page."""
        pass

    @abstractmethod
    def get_article_title(self, article):
        """Returns the title of an article."""
        pass

    @abstractmethod
    def get_article_link(self, article):
        """Returns the link of an article."""
        pass

    def get_article_date_posted(self, article):
        """Returns the date an article was posted."""
        pass

    def get_timestamp(self, date_posted):
        """Returns a timestamp from an ISO date. This may be overridden in
        subclasses
        """
        print("BC GET TIMESTAMP")
        return datetime.datetime.strptime(
            date_posted, "%Y-%m-%dT%H:%M:%S%z"
        ).timestamp()

    def get_full_text_and_date_posted(self, article):
        """Returns text and last updated simultaneously"""
        pass

    def get_article_full_text(self, article_link):
        """Returns the text of an article."""
        pass

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

        if stop_timestamp and current_timestamp > stop_timestamp:
            return True

        return False
