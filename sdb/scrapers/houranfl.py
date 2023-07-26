from sdb.scrapers.base_scraper import BaseScraper
import sdb.scrapers.utils as utils
from sdb.scrapers.scraping_error import ScrapingError
from sdb.scrapers.scrape_result import ScrapeResult

import time
import datetime


class HouranFL(BaseScraper):
    def __init__(self):
        self.url_template = "https://www.horanfree.com/page/{page_num}?cat=%2A"
        self.publication = "Houran Free League"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of HFL articles until time limit reached."""

        # Dataclass scrape result to be returned
        scrape_result = ScrapeResult()
        url = self.url_template

        while True:
            # Generate correct url from template
            url = url.format(page_num=page_num)

            # bs4 setup
            try:
                soup = self.get_soup(url=url)
            except ScrapingError as e:
                print(f"Scraping error: {e}")
                scrape_result.success = False
                scrape_result.error_message = str(e)
                return scrape_result

            articles = soup.find_all("li", class_="post-item")

            count = 1

            # Gathers article info for each post on single page
            for a in articles:
                # identifies date posted and generates Unix timestamp
                date_posted = a.find("span", class_="date meta-item tie-icon").text
                current_timestamp = self.get_timestamp_from_arabic_latin_date_HFL(
                    date_posted
                )
                link = a.find("a", class_=None).get("href")

                # Breaks loop if timestamp reached
                if self.reached_time_limit_loop(
                    stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
                ):
                    return scrape_result

                # Gets title and basic data and creates dict for article
                article = {
                    "date_posted": current_timestamp,
                    "title": a.find("h2", class_="post-title").text,
                    "link": link,
                    "publication": self.publication,
                }

                # Adds dict attribute for article text then appends to article_list
                try:
                    article["full_text"] = self.get_article_text(article["link"])
                except ScrapingError as e:
                    print(f"Scraping error: {e}")
                    scrape_result.success = False
                    scrape_result.error_message = str(e)
                    return scrape_result

                # Send console message
                self.entry_added_message(count=count, page_num=page_num)
                count += 1
                scrape_result.article_list.append(article)

            # Checks if stop timestamp reached.
            if not self.should_continue_pagination(
                stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
            ):
                return scrape_result

            # Go to next page
            page_num = page_num + 1

            # Send console message
            self.next_page_message(count=count, page_num=page_num)

            if page_num > 2:
                url = "dddddd"

    def get_article_text(self, article_link):
        """Gathers article text content from link to given article. Concatenates all
        paragraph elements into single string and returns it."""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # iterates thru paragraphs and concatenates text content
        paragraphs = soup.find("div", class_="entry-content entry clearfix").find_all(
            "p", recursive=False
        )
        return "\n\n".join(paragraph.text for paragraph in paragraphs)

    def get_timestamp_from_arabic_latin_date_HFL(self, date):
        """Converts Arabic date in 'dd, m, YYYY' format to unix timestamp"""

        # Get number of Arabic month and replace it in string
        for month in utils.ARABIC_LATIN_MONTHS:
            if month in date:
                translated_date = date.replace(month, utils.ARABIC_LATIN_MONTHS[month])

        # Get unix timestamp from translated date
        return time.mktime(
            datetime.datetime.strptime(translated_date, "%d %m، %Y").timetuple()
        )
