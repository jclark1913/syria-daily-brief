from syriadailybrief.scrapers.base_scraper import Base_Scraper
import syriadailybrief.scrapers.utils as utils

import time
import datetime


class HouranFL(Base_Scraper):
    def __init__(self):
        self.url_template = "https://www.horanfree.com/page/{page_num}?cat=%2A"
        self.publication = "Houran Free League"

    def get_news_articles_by_page(self, page_num=1, stop_timestamp=False):
        """Scrapes a single page of HFL articles until time limit reached."""

        # Generate correct url from template
        url = self.url_template.format(page_num=page_num)

        # bs4 setup
        soup = self.get_soup(url=url)
        articles = soup.find_all("li", class_="post-item")

        # List of articles to be returned
        article_list = []

        count = 1

        # Gathers article info for each post on single page
        for a in articles:
            # identifies date posted and generates Unix timestamp
            date_posted = a.find("span", class_="date meta-item tie-icon").text
            current_timestamp = self.get_timestamp_from_arabic_latin_date(date_posted)
            link = a.find("a", class_=None).get("href")

            # Breaks loop if timestamp reached
            if self.reached_time_limit_loop(
                stop_timestamp=stop_timestamp, current_timestamp=current_timestamp
            ):
                break

            # Gets title and basic data and creates dict for article
            article = {
                "date_posted": current_timestamp,
                "title": a.find("h2", class_="post-title").text,
                "link": link,
                "publication": self.publication,
                "full_text": self.get_article_text(link),
            }

            # Send console message
            self.entry_added_message(count=count, page_num=page_num)
            count += 1
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
        """Gathers article text content from link to given article. Concatenates all
        paragraph elements into single string and returns it."""

        # bs4 setup
        soup = self.get_soup(url=article_link)

        # iterates thru paragraphs and concatenates text content
        paragraphs = soup.find("div", class_="entry-content entry clearfix").find_all(
            "p", recursive=False
        )
        return "\n\n".join(paragraph.text for paragraph in paragraphs)

    def get_timestamp_from_arabic_latin_date(self, date):
        """Converts Arabic date in 'dd, m, YYYY' format to unix timestamp"""

        # Get number of Arabic month and replace it in string
        for month in utils.ARABIC_LATIN_MONTHS:
            if month in date:
                translated_date = date.replace(month, utils.ARABIC_LATIN_MONTHS[month])

        # Get unix timestamp from translated date
        return time.mktime(
            datetime.datetime.strptime(translated_date, "%d %m، %Y").timetuple()
        )
