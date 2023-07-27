from sdb.scrapers.base_scraper import BaseScraper
from sdb.scrapers.scrape_result import ScrapeResult
from sdb.scrapers.scraping_error import ScrapingError

import datetime

# import syriadailybrief.scrapers.utils as utils


class SyriaDirect(BaseScraper):
    def __init__(self):
        self.url_template = "https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/{page_num}/?lang=ar"
        self.publication = "Syria Direct"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of Syria Direct articles until time limit reached"""

        # Dataclass scrape result to be returned
        scrape_result = ScrapeResult()
        url_template = self.url_template

        while True:
            url = url_template.format(page_num=page_num)

            try:
                # bs4 setup
                soup = self.get_soup(url=url)
            except ScrapingError as e:
                print(f"Scraping error: {e}")
                scrape_result.success = False
                scrape_result.error_message = str(e)
                return scrape_result

            articles = soup.find("div", class_="fusion-posts-container").find_all(
                "article"
            )

            count = 1

            # Gathers article info for each post on single page
            for a in articles:
                date_posted = a.find("span", class_="updated").text
                current_timestamp = self.get_timestamp(date_posted)

                # Returns result if timestamp reached
                if self.reached_time_limit_loop(
                    stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
                ):
                    return scrape_result

                title = a.find("h2").find("a").text
                article = {
                    "date_posted": current_timestamp,
                    "title": title,
                    "publication": self.publication,
                    "link": a.find("h2").find("a").get("href"),
                }

                # Send console message
                self.entry_added_message(count=count, page_num=page_num)
                count += 1

                # Add dict attribute for article text then append to article_list
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
        """Concatenates all paragraph elements in article into a single string,
        returns it"""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # Identifies paragraphs and creates empty variable for text content
        paragraphs = soup.find("div", class_="sd_article_body").find_all(
            "p", recursive=False
        )
        text_content = ""

        # Iterates thru paragraph elements and concatenates all elements containing text
        for paragraph in paragraphs:
            elements = paragraph.find_all(True)
            for element in elements:
                text_content = text_content + element.text
            text_content = text_content + "\n\n"

        return text_content

    def get_timestamp(self, date):
        """Takes date input and converts it to Unix timestamp.

        NOTE: Assumes date is in ISO 8601 format.
        """

        return int(datetime.datetime.fromisoformat(date).timestamp())
