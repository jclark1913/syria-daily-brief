import time
import datetime

from base_scraper import Base_Scraper


class SANA_Scraper(Base_Scraper):
    def __init__(self):
        self.url_template = "https://sana.sy/?cat=29582&paged={page_num}"
        self.publication = "SANA (Syrian Arab News Network)"

    # def get_data(self, stop_timestamp):

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of sana articles until time limit reached
        TODO: Handle server timeout while looping
        """

        # Generate correct url from template
        url = self.url_template.format(page_num)
        print(url)

        # bs4 setup
        soup = self.get_soup(url=url)



    def get_article_text(self, article_link):
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