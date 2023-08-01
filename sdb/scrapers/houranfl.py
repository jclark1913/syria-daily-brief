from sdb.scrapers.base_scraper import BaseScraper, ScraperConfig

import datetime
import json

HouranFL_config = ScraperConfig(
    url_template="https://www.horanfree.com/page/{page_num}?cat=%2A",
    publication="Houran Free League",
    can_get_metadata_from_page=False,
)


class HouranFL(BaseScraper):
    def __init__(self):
        self.config = HouranFL_config

    def find_all_articles(self, soup):
        """Returns all articles on a page."""

        return soup.find_all("li", class_="post-item")

    def find_article_title(self, article):
        """Returns title of article."""

        return article.find("h2", class_="post-title").text

    def find_article_link(self, article):
        """Returns link to article."""

        return article.find("a", class_=None).get("href")

    def get_article_text_and_last_updated(self, article_link):
        """Gathers article text content from link to given article. Concatenates all
        paragraph elements into single string and returns it."""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # Get last updated date
        script = soup.find("script", id="tie-schema-json")

        # Load script as json
        data = json.loads(script.text)

        # Get last updated date
        last_updated = data["dateCreated"]

        # iterates thru paragraphs and concatenates text content
        paragraphs = soup.find("div", class_="entry-content entry clearfix").find_all(
            "p", recursive=False
        )

        full_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

        return last_updated, full_text

    def get_timestamp(self, date_posted):
        """Gets the timestamp of an article"""

        return datetime.datetime.strptime(
            date_posted, "%Y-%m-%dT%H:%M:%S%z"
        ).timestamp()
