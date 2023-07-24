import datetime

from syriadailybrief.scrapers.base_scraper import Base_Scraper
# import syriadailybrief.scrapers.utils as utils


class SyriaDirect(Base_Scraper):
    def __init__(self):
        self.url_template = "https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/{page_num}/?lang=ar"
        self.publication = "Syria Direct"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of Syria Direct articles until time limit reached"""

        # Generate correct url from template
        url = self.url_template.format(page_num=page_num)

        # bs4 setup
        soup = self.get_soup(url=url)
        articles = soup.find("div", class_="fusion-posts-container").find_all("article")

        # List of articles to be returned
        article_list = []

        count = 1

        # Gathers article info for each post on single page
        for a in articles:
            date_posted = a.find("span", class_="updated").text
            current_timestamp = self.get_timestamp(date_posted)

            # Breaks loop if timestamp reached
            if self.reached_time_limit_loop(
                stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
            ):
                break

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
            article["full_text"] = self.get_article_text(article["link"])
            article_list.append(article)

        # Recursively calls method for next page until stop_timestamp reached.
        if self.reached_time_limit_recurse(
            stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
        ):
            next_page_num = page_num + 1

            # Send console message
            self.next_page_message(count=count, page_num=next_page_num)

            article_list += self.get_news_articles_by_page(
                page_num=next_page_num, stop_timestamp=stop_timestamp
            )

        return article_list

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
