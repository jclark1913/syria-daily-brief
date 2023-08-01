from sdb.scrapers.base_scraper import BaseScraper, ScraperConfig

Suwayda24_Config = ScraperConfig(
    url_template="https://suwayda24.com/?cat=%2A&paged={page_num}",
    publication="Suwayda 24",
    should_get_metadata_during_pagination=False,
)


class Suwayda24(BaseScraper):
    def __init__(self):
        self.config = Suwayda24_Config

    def get_all_articles(self, soup):
        """Finds all articles on a single page"""

        articles = soup.find("div", class_="post-listing archive-box").find_all(
            "article"
        )
        return articles[:10]

    def get_article_title(self, article):
        """Finds the title of an article"""

        return article.find("h2", class_="post-box-title").text

    def get_article_link(self, article):
        """Finds the link of an article"""

        return article.find("h2", class_="post-box-title").find("a").get("href")

    def get_full_text_and_date_posted(self, article_link):
        """Gets text and last updated date from article"""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # Get script w/ date object
        date_posted = soup.find("meta", property="article:published_time").get(
            "content"
        )

        # Identifies paragraphs and creates empty variable for text content
        paragraphs = soup.find("div", class_="entry").find_all("p", recursive=False)
        full_text = "\n\n".join(paragraph.text for paragraph in paragraphs)

        return date_posted, full_text
