from sdb.scrapers.base_scraper import BaseScraper, ScraperConfig

import time
import datetime

SANA_config = ScraperConfig(
    url_template="https://sana.sy/?cat=29582&paged={page_num}",
    publication="SANA (Syrian Arab News Agency)",
    should_get_metadata_during_pagination=True,
)


class SANA(BaseScraper):
    def __init__(self):
        self.config = SANA_config

    def get_all_articles(self, soup):
        """Finds all articles on a single page and returns them as a list."""

        return soup.find_all("article", class_="item-list")

    def get_article_title(self, article):
        """Returns the title of an article."""

        return article.find("a", class_=None).text

    def get_article_link(self, article):
        """Returns the link of an article."""

        return article.find("a", class_="more-link").get("href")

    def get_article_date_posted(self, article):
        """Returns the date posted of an article."""

        return article.find("span", class_="tie-date").text

    def get_article_full_text(self, article_link):
        """Concatenates all paragraph elements in article into a single string and
        returns it"""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # iterates thru paragraphs and concatenates text content
        paragraphs = soup.find("div", class_="entry").find_all("p", recursive=False)
        return "\n\n".join(paragraph.text for paragraph in paragraphs)

    def get_timestamp(self, date):
        """Takes date input and converts it to Unix timestamp

        NOTE: Assumes date is in YYYY-mm-dd format.
        """

        # Uses time and datetime libs to generate Unix timestamp
        return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())

