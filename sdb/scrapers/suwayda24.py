from sdb.scrapers.base_scraper import BaseScraper
from sdb.scrapers.scraping_error import ScrapingError
from sdb.scrapers.scrape_result import ScrapeResult
import sdb.scrapers.utils as utils

import time
import datetime


class Suwayda24(BaseScraper):
    def __init__(self):
        self.url_template = "https://suwayda24.com/?cat=%2A&paged={page_num}"
        self.publication = "Suwayda 24"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of Suwayda24 articles until time limit is reached."""

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

            articles = soup.find("div", class_="post-listing archive-box").find_all(
                "article"
            )

            count = 1

            for a in articles:
                # Get article link
                content = a.find("h2", class_="post-box-title")
                link = content.find("a").get("href")
                last_updated = a.find("span", class_="tie-date").text

                # Get current timestamp for article. NOTE: This checks to see if the
                # unicode right-to-left character is in the span. If not, s24 is
                # using a numeric date.
                if "\u200f" in last_updated:
                    current_timestamp = utils.get_approx_timestamp_from_last_updated_AR(
                        last_updated
                    )
                else:
                    current_timestamp = self.get_s24_eng_timestamp(last_updated)

                # Verifies that current_timestamp is less than (earlier than) limit,
                # breaks loop if so.
                if self.reached_time_limit_loop(
                    stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
                ):
                    return scrape_result

                article = {
                    "date_posted": current_timestamp,
                    "title": content.text,
                    "publication": self.publication,
                    "link": link,
                }

                try:
                    article["text"] = self.get_article_text(article_link=link)
                except ScrapingError as e:
                    print(f"Scraping error: {e}")
                    scrape_result.success = False
                    scrape_result.error_message = str(e)
                    return scrape_result

                self.entry_added_message(count=count, page_num=page_num)
                count += 1
                scrape_result.article_list.append(article)
                if count > 10:
                    break

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
        article_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

        return article_text

    def get_s24_eng_timestamp(self, last_updated):
        """Returns a unix timestamp for mm/dd/Y timestamps"""

        return time.mktime(
            datetime.datetime.strptime(last_updated, "%m/%d/%Y").timetuple()
        )
