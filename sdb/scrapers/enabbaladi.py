from sdb.scrapers.base_scraper import BaseScraper, ScraperConfig

import datetime

EnabBaladi_Config = ScraperConfig(
    url_template="https://www.enabbaladi.net/archives/category/online/page/{page_num}",
    publication="Enab Baladi",
    can_get_metadata_from_page=False,
)


class EnabBaladi(BaseScraper):
    def __init__(self):
        self.config = EnabBaladi_Config

    def find_all_articles(self, soup):
        """Returns a list of all article elements on page."""

        return soup.find_all("div", class_="one-post")

    def find_article_title(self, article):
        """Returns article title."""

        return article.find("div", class_="item-content").find("a").find("h3").text

    def find_article_link(self, article):
        """Returns article link."""

        return article.find("div", class_="item-content").find("a").get("href")

    def get_article_text_and_last_updated(self, article_link):
        """Returns full text and last_updated"""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # Gets last updated timestamp from metadata
        last_updated = soup.find("meta", property="article:published_time").get(
            "content"
        )

        # Identifies paragraphs and creates empty variable for text content
        paragraphs = soup.find("div", class_="content-article").find_all(
            "p", recursive=False
        )

        # Concatenates all paragraph elements in article into single string
        full_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

        return last_updated, full_text

    def get_timestamp(self, date_posted):
        """Returns timestamp from date_posted."""
        return datetime.datetime.strptime(
            date_posted, "%Y-%m-%dT%H:%M:%S%z"
        ).timestamp()
