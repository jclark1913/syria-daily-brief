from sdb.scrapers.base_scraper import BaseScraper
import sdb.scrapers.utils as utils
from sdb.scrapers.scraping_error import ScrapingError
from sdb.scrapers.scrape_result import ScrapeResult

import time


class EnabBaladi(BaseScraper):
    def __init__(self):
        self.url_template = (
            "https://www.enabbaladi.net/archives/category/online/page/{page_num}"
        )
        self.publication = "Enab Baladi"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of Enab Beladi articles until time limit reached.
        TODO: Handle server timeout while looping

        NOTE: There is a peculiarity with Enab Beladi. The most recent 5-6 articles
        are "featured", and they don't have dates attached to their parent elements
        on page 1. I could circumvent this by getting their dates when I get the
        full text of the article, but for now I will assume that featured articles
        are from today (Enab Beladi is prolific and publishes 20+ articles each day)
        """

        # Dataclass scrape result to be returned
        scrape_result = ScrapeResult()
        url_template = self.url_template

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

            articles = soup.find_all("div", class_="one-post")

            count = 1

            # Gathers article info for each post on single page
            for a in articles:
                content = a.find("div", class_="item-content")

                # The top featured articles do not have a timestamp on the main page, so
                # we assume that the top 5-6 featured articles are from today.
                if content.find("samp"):
                    current_timestamp = utils.get_timestamp_from_arabic_latin_date(
                        content.find("samp").text
                    )
                    date_posted = current_timestamp
                else:
                    current_timestamp = int(time.time())
                    date_posted = current_timestamp

                # Breaks loop if timestamp reached
                if self.reached_time_limit_loop(
                    stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
                ):
                    return scrape_result

                title = content.find("a").find("h3").text

                # Generates article object w/ date posted using datetime.fromtimestamp
                article = {
                    "date_posted": date_posted,
                    "title": title,
                    "publication": self.publication,
                    "link": a.find("a").get("href"),
                }

                self.entry_added_message(count=count, page_num=page_num)
                count += 1

                # Adds dict attribute for article text then appends to article_list
                try:
                    article["full_text"] = self.get_article_text(article["link"])
                except ScrapingError as e:
                    print(f"Scraping error: {e}")
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
        """Concatenates all paragraph elements in article into single string and
        returns it."""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # Identifies paragraphs and creates empty variable for text content
        paragraphs = soup.find("div", class_="content-article").find_all(
            "p", recursive=False
        )
        return "\n\n".join(paragraph.text for paragraph in paragraphs)
