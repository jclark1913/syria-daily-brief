from sdb.scrapers.base_scraper import BaseScraper, ScraperConfig
from sdb.scrapers.scrape_result import ScrapeResult
from sdb.scrapers.scraping_error import ScrapingError

import datetime

SyriaDirect_Config = ScraperConfig(
    url_template="https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/{page_num}/?lang=ar",
    publication="Syria Direct",
    can_get_metadata_from_page=True,
)

class SyriaDirect(BaseScraper):
    def __init__(self):
        self.config = SyriaDirect_Config

    def find_all_articles(self, soup):
        """Finds all articles on a single page"""

        return soup.find("div", class_="fusion-posts-container").find_all("article")

    def find_article_title(self, article):
        """Find title of article"""

        return article.find("h2").find("a").text

    def find_article_link(self, article):
        """Find link of article"""

        return article.find("h2").find("a").get("href")

    def find_article_date_posted(self, article):
        """Returns the date posted of an article"""

        return article.find("span", class_="updated").text

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

    def get_timestamp(self, date_posted):
        """Gets the timestamp of an article"""

        return datetime.datetime.strptime(
            date_posted, "%Y-%m-%dT%H:%M:%S%z"
        ).timestamp()
