from sdb.scrapers.base_scraper import BaseScraper, ScraperConfig
import sdb.scrapers.utils as utils
from sdb.scrapers.scrape_result import ScrapeResult
from sdb.scrapers.scraping_error import ScrapingError

DEZ24_Config = ScraperConfig(
    url_template="https://deirezzor24.net/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1/page/{page_num}/",
    publication="Deir Ezzor 24",
    can_get_metadata_from_page=False,
)

class DEZ24(BaseScraper):
    def __init__(self):
        self.config = DEZ24_Config

    def find_all_articles(self, soup):
        """Finds all articles on a single page"""

        articles = soup.find("div", class_="vce-loop-wrap").find_all("article")
        return articles

    def find_article_title(self, article):
        """Finds the title of an article"""

        content = article.find("h2", class_="entry-title")
        title = content.find("a").text
        return title

    def find_article_link(self, article):
        """Finds the link of an article"""

        content = article.find("h2", class_="entry-title")
        link = content.find("a").get("href")
        return link

    def find_article_date_posted(self, article):
        """Gets the date posted of an article"""

        return article.find("span", class_="updated").text

    def get_timestamp(self, date_posted):
        """Gets the timestamp of an article"""

        return utils.get_approx_timestamp_from_last_updated_AR(date_posted)

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
        full_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

        # Get last_updated to generate timestamp
        last_updated = soup.find("span", class_="updated").text

        return last_updated, full_text
