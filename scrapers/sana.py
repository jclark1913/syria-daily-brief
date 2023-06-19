import requests
from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS

def get_sana_data(lower_time_limit):
    """Scrapes sana.sy and collects all posts up to a given time limit. Returns
    all this data as object"""


def get_news_articles_by_page(page_num):
    """Scrapes a single page of sana articles until time limit reached"""

def get_article_text(article_link):
    """Concatenates all paragraph elements in article into a single string and
    returns it"""

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # iterates thru paragraphs and concatenates text content
    paragraphs = soup.find('div', class_='entry').find_all('p', recursive=False)
    return "\n\n".join(paragraph.text for paragraph in paragraphs)

