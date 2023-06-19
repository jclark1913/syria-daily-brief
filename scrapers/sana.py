import requests
from bs4 import BeautifulSoup
from globalscrape import DEFAULT_HEADERS


def get_sana_data(lower_time_limit):
    """Scrapes sana.sy and collects all posts up to a given time limit. Returns
    all this data as object"""


def get_news_articles_by_page(page_num=1):
    """Scrapes a single page of sana articles until time limit reached"""

    # bs4 setup
    response = requests.get(f"https://sana.sy/?cat=29582&paged={page_num}",
                            headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article', class_='item-list')

    # List of articles to be returned
    article_list = []

    # Gathers article info for each post on single page
    for a in articles:

        # Gets title from card + creates dict of basic data
        title = a.find('a', class_=None).text
        article = {
            'title': title,
            'timestamp': a.find('span', class_='tie-date').text,
            'link': a.find('a', class_='more-link').get('href'),
        }

        # Adds dict attribute for article text then appends to article_list
        article['full_text'] = get_article_text(article['link'])
        article_list.append(article)

    return article_list


def get_article_text(article_link):
    """Concatenates all paragraph elements in article into a single string and
    returns it"""

    # bs4 setup
    response = requests.get(article_link, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # iterates thru paragraphs and concatenates text content
    paragraphs = soup.find('div', class_='entry').find_all(
        'p', recursive=False)
    return "\n\n".join(paragraph.text for paragraph in paragraphs)
