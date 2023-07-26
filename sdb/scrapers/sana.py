from sdb.scrapers.base_scraper import BaseScraper
from sdb.scrapers.scraping_error import ScrapingError
from sdb.scrapers.scrape_result import ScrapeResult

import time
import datetime


class SANA(BaseScraper):
    def __init__(self):
        self.url_template = "https://sana.sy/?cat=29582&paged={page_num}"
        self.publication = "SANA (Syrian Arab News Network)"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of SANA articles until time limit reached"""

        # Dataclass scrape result to be returned
        scrape_result = ScrapeResult()

        url = self.url_template

        while True:
            # Generate correct url from template
            url = url.format(page_num=page_num)

            # This try/except block is used to catch any errors that occur during
            # scraping and return the article_list up to that point.
            try:
                # bs4 setup
                soup = self.get_soup(url=url)
            except ScrapingError as e:
                print(f"Scraping error: {e}")
                scrape_result.success = False
                scrape_result.error_message = str(e)
                return scrape_result

            articles = soup.find_all("article", class_="item-list")

            count = 1

            # Gathers article info for each post on single page
            for a in articles:
                # identifies date posted and generates Unix timestamp
                date_posted = a.find("span", class_="tie-date").text
                current_timestamp = self.get_timestamp_SANA(date_posted)

                # Breaks loop if timestamp reached
                if self.reached_time_limit_loop(
                    stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
                ):
                    return scrape_result

                # Gets title from card + creates dict of basic data
                title = a.find("a", class_=None).text
                article = {
                    "date_posted": current_timestamp,
                    "title": title,
                    "publication": self.publication,
                    "link": a.find("a", class_="more-link").get("href"),
                }

                # Send console message
                self.entry_added_message(count=count, page_num=page_num)
                count += 1

                # Adds dict attribute for article text then appends to article_list.
                try:
                    article["full_text"] = self.get_article_text(article["link"])
                except ScrapingError as e:
                    print("Scraping error: {e}")
                    scrape_result.success = False
                    scrape_result.error_message = str(e)
                    return scrape_result

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

    def get_article_text(self, article_link):
        """Concatenates all paragraph elements in article into a single string and
        returns it"""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # iterates thru paragraphs and concatenates text content
        paragraphs = soup.find("div", class_="entry").find_all("p", recursive=False)
        return "\n\n".join(paragraph.text for paragraph in paragraphs)

    def get_timestamp_SANA(self, date):
        """Takes date input and converts it to Unix timestamp

        NOTE: Assumes date is in YYYY-mm-dd format.
        """

        # Uses time and datetime libs to generate Unix timestamp
        return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
