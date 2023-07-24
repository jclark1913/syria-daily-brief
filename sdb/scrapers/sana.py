from sdb.scrapers.base_scraper import Base_Scraper

# import syriadailybrief.scrapers.utils as utils

import time
import datetime


class SANA(Base_Scraper):
    def __init__(self):
        self.url_template = "https://sana.sy/?cat=29582&paged={page_num}"
        self.publication = "SANA (Syrian Arab News Network)"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of SANA articles until time limit reached"""

        # Generate correct url from template
        url = self.url_template.format(page_num=page_num)

        # bs4 setup
        soup = self.get_soup(url=url)
        articles = soup.find_all("article", class_="item-list")

        # List of articles to be returned
        article_list = []

        count = 1

        # Gathers article info for each post on single page
        for a in articles:
            # identifies date posted and generates Unix timestamp
            date_posted = a.find("span", class_="tie-date").text
            current_timestamp = self.get_timestamp_SANA(date_posted)

            # Breaks loop if timestamp reached
            if self.reached_time_limit_loop(
                stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
            ):
                break

            # Gets title from card + creates dict of basic data
            title = a.find("a", class_=None).text
            article = {
                "date_posted": current_timestamp,
                "title": title,
                "publication": self.publication,
                "link": a.find("a", class_="more-link").get("href"),
            }

            # Send console message
            self.entry_added_message(count=count, page_num=page_num)
            count += 1

            # Adds dict attribute for article text then appends to article_list
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
        """Concatenates all paragraph elements in article into a single string and
        returns it"""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # iterates thru paragraphs and concatenates text content
        paragraphs = soup.find("div", class_="entry").find_all("p", recursive=False)
        return "\n\n".join(paragraph.text for paragraph in paragraphs)

    def get_timestamp_SANA(self, date):
        """Takes date input and converts it to Unix timestamp

        NOTE: Assumes date is in YYYY-mm-dd format.
        """

        # Uses time and datetime libs to generate Unix timestamp
        return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
