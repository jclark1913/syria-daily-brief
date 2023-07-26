from sdb.scrapers.base_scraper import BaseScraper
import sdb.scrapers.utils as utils
from sdb.scrapers.scrape_result import ScrapeResult
from sdb.scrapers.scraping_error import ScrapingError


class DEZ24(BaseScraper):
    def __init__(self):
        self.url_template = "https://deirezzor24.net/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1/page/{page_num}/"
        self.publication = "Deir Ezzor 24"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of DEZ24 articles"""

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

            articles = soup.find("div", class_="vce-loop-wrap").find_all("article")

            count = 1

            # Gathers article info for each post on a single page
            for a in articles:
                # Get article link
                content = a.find("h2", class_="entry-title")
                link = content.find("a").get("href")

                # Destructure last_updated and article_text
                [last_updated, article_text] = list(
                    self.get_article_text_and_last_updated(link).values()
                )

                # Get current timestamp for article
                try:
                    current_timestamp = utils.get_approx_timestamp_from_last_updated_AR(
                        last_updated
                    )
                except ScrapingError as e:
                    print(f"Scraping error: {e}")
                    scrape_result.success = False
                    scrape_result.error_message = str(e)
                    return scrape_result

                # Breaks loop if timestamp reached
                if self.reached_time_limit_loop(
                    stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
                ):
                    return scrape_result

                article = {
                    "date_posted": current_timestamp,
                    "title": content.text,
                    "publication": self.publication,
                    "link": link,
                    "full_text": article_text,
                }

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

    def get_article_text_and_last_updated(self, article_link):
        """Gets the text from a single article as well as the description in
        Arabic showing how recently the article was published.
        """

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # Identifies paragraphs and creates empty variable for text content
        paragraphs = soup.find("div", class_="entry-content").find_all(
            "p", recursive=False
        )
        article_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

        # Get last_updated to generate timestamp
        last_updated = soup.find("span", class_="updated").text

        return {"last_updated": last_updated, "article_text": article_text}
