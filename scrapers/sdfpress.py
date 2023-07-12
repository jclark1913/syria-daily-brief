# NOTE: Currently not functioning due to cloudfare ddos protection

# import requests

# import time
# import datetime
# import cfscrape

# from bs4 import BeautifulSoup
# from globalscrape import DEFAULT_HEADERS, ARABIC_LATIN_MONTHS

# def get_sdfpress_data(date):
#     """"""

# def get_news_articles_by_page(page_num=1, stop_timestamp=False):
#     """"""

#     # bs4 setup
#     # response = requests.get(
#     #     f"https://sdf-press.com/?s&paged={page_num}", headers=DEFAULT_HEADERS
#     # )
#     # soup = BeautifulSoup(response.content, "html.parser")

#     scraper = cfscrape.create_scraper(delay=10)
#     print(scraper.get(f"https://sdf-press.com/?s&paged={page_num}").content)


#     # print(response.content)
#     # print("Response received. Waiting 10 secs...")
#     # time.sleep(1)

#     articles = soup.find_all("article", class_="listing-item")
#     print("Articles collected. Waiting 10 secs...")
#     time.sleep(1)

#     # List of articles to be returned
#     article_list = []

#     count = 1

#     for a in articles:
#         date_posted = a.find("time", class_="post-published")
#         title = a.find("a", class_="post-title").text
#         article = {
#             "title": title,
#             "date_posted": date_posted,
#             "link": a.find("a", class_="post-url").get("href")
#         }

#         print(count)
#         count += 1

#         article_list.append(article)

#     return article_list

# def get_article_text(article_link):
#     """"""

# def get_timestamp(date):
#     """Converts Arabic date in 'YYYY, dd month' format to unix timestamp"""

#     # Get number of Arabic month and replace it in string
#     for month in ARABIC_LATIN_MONTHS:
#         if month in date:
#             translated_date = date.replace(month, ARABIC_LATIN_MONTHS[month])

#     # Get unix timestamp from translated date
#     return time.mktime(datetime.datetime.strptime(translated_date, "%m %d, %Y").timetuple())








