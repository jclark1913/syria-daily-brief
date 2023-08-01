from sdb.scrapers.base_scraper import BaseScraper, ScraperConfig
import json

HouranFL_config = ScraperConfig(
    url_template="https://www.horanfree.com/page/{page_num}?cat=%2A",
    publication="Houran Free League",
    should_get_metadata_during_pagination=False,
)


class HouranFL(BaseScraper):
    def __init__(self):
        self.config = HouranFL_config

    def get_all_articles(self, soup):
        """Returns all articles on a page."""

        return soup.find_all("li", class_="post-item")

    def get_article_title(self, article):
        """Returns title of article."""

        return article.find("h2", class_="post-title").text

    def get_article_link(self, article):
        """Returns link to article."""

        return article.find("a", class_=None).get("href")

    def get_full_text_and_date_posted(self, article_link):
        """Gathers article text content from link to given article. Concatenates all
        paragraph elements into single string and returns it."""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # Get last updated date
        script = soup.find("script", id="tie-schema-json")

        # Load script as json
        data = json.loads(script.text)

        # Get last updated date
        date_posted = data["dateCreated"]

        # iterates thru paragraphs and concatenates text content
        paragraphs = soup.find("div", class_="entry-content entry clearfix").find_all(
            "p", recursive=False
        )

        full_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

        return date_posted, full_text
