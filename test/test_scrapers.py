from unittest import TestCase, mock
from bs4 import BeautifulSoup

# import every file from scrapers directory

from sdb.scrapers.scraping_error import ScrapingError
from sdb.scrapers.scrape_result import ScrapeResult
from sdb.scrapers.base_scraper import ScraperConfig

from sdb.scrapers import (
    base_scraper,
    dez24,
    enabbaladi,
    houranfl,
    sana,
    suwayda24,
    syriadirect,
)


class BaseScraperTestCase(TestCase):
    """Tests for base_scraper.py"""

    def test_is_abstract_class(self):
        """Is BaseScraper an abstract class?"""

        """Should raise TypeError when attempting to instantiate BaseScraper"""
        with self.assertRaises(TypeError):
            base_scraper.BaseScraper()

    def test_get_soup_invalid(self):
        """Does get_soup with an invalid url raise a ScrapingError?"""

        test_scraper = dez24.DEZ24()

        """Should raise ScrapingError when passed invalid url"""
        with self.assertRaises(ScrapingError):
            test_scraper.get_soup(url="https://invalid-url.sy")

    def test_reached_time_limit_loop(self):
        """Does reached_time_limit_loop return correct boolean?"""

        test_scraper = dez24.DEZ24()

        """Should return True if current_timestamp is less than stop_timestamp"""
        self.assertTrue(
            test_scraper.reached_time_limit_loop(
                stop_timestamp=1000, current_timestamp=1
            )
        )

        """Should return False if current_timestamp is less than stop_timestamp"""
        self.assertFalse(
            test_scraper.reached_time_limit_loop(
                stop_timestamp=1, current_timestamp=1000
            )
        )

        """Should return False if stop_timestamp is not passed into method"""
        self.assertFalse(test_scraper.reached_time_limit_loop(current_timestamp=1000))

    def test_should_continue_pagination(self):
        """Does should_continue_pagination return correct boolean?"""

        test_scraper = dez24.DEZ24()

        """Should return True if current_timestamp is greater than stop_timestamp"""
        self.assertTrue(
            test_scraper.should_continue_pagination(
                stop_timestamp=1, current_timestamp=1000
            )
        )

        """Should return false if current_timestamp is less than stop_timestamp"""
        self.assertFalse(test_scraper.should_continue_pagination(1000, 1))

        """Shoulre return False if stop_timestamp is not passed into method"""
        self.assertFalse(
            test_scraper.should_continue_pagination(current_timestamp=1000)
        )

    def test_get_timestamp(self):
        """Does get_timestamp convert ISO to unix timestamp?"""

        test_scraper = dez24.DEZ24()

        """Should return correct unix timestamp"""
        self.assertEqual(
            test_scraper.get_timestamp("2023-07-23T13:03:36+00:00"), 1690117416
        )


class DEZ24TestCase(TestCase):
    """Test for dez24.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.dez24 = dez24.DEZ24()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does DEZ24 have correct config properties?"""

        self.assertEqual(
            self.dez24.config.url_template,
            "https://deirezzor24.net/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1/page/{page_num}/",
        )
        self.assertEqual(self.dez24.config.publication, "Deir Ezzor 24")
        self.assertEqual(self.dez24.config.should_get_metadata_during_pagination, False)

    def test_get_soup(self):
        """Does DEZ24.get_soup return a BeautifulSoup object?"""

        soup = self.dez24.get_soup(
            url="https://deirezzor24.net/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1/page/1/"
        )
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return dataclass with correct info?"""

        scrape_result = self.dez24.get_news_articles_by_page(page_num=1)

        """Does get_news_articles_by_page return ScrapeResult dataclass?"""
        self.assertTrue(isinstance(scrape_result, ScrapeResult))

        """Does ScrapeResult indicate success and contain an article list?"""
        self.assertTrue(scrape_result.success)
        self.assertEqual(len(scrape_result.article_list), 10)

    def test_get_full_text_and_date_posted(self):
        """Does get_full_text_and_date_posted return correct data?"""

        [date_posted, full_text] = self.dez24.get_full_text_and_date_posted(
            "https://deirezzor24.net/%d8%b9%d9%86%d8%a7%d8%b5%d8%b1-%d8%a7%d9%84%d9%81%d9%8a%d9%84%d9%82-%d8%a7%d9%84%d8%ae%d8%a7%d9%85%d8%b3-%d8%a8%d8%af%d9%8a%d8%b1%d8%a7%d9%84%d8%b2%d9%88%d8%b1-%d9%8a%d9%87%d8%af%d8%af%d9%88%d9%86/"
        )

        """Does get_full_text_and_date_posted return correct date_posted?"""
        self.assertEqual(date_posted, "2023-07-23T18:19:32+00:00")

        """Does get_full_text_and_date_posted return correct full_text?"""
        self.assertTrue(type(full_text) is str)
        self.assertTrue(len(full_text) > 0)


class EnabBaladiTestCase(TestCase):
    """Tests for enabbaladi.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.enabbaladi = enabbaladi.EnabBaladi()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does EnabBaladi have correct url_template and publication properties?"""

        self.assertEqual(
            self.enabbaladi.config.url_template,
            "https://www.enabbaladi.net/archives/category/online/page/{page_num}",
        )
        self.assertEqual(self.enabbaladi.config.publication, "Enab Baladi")
        self.assertEqual(
            self.enabbaladi.config.should_get_metadata_during_pagination, False
        )

    def test_get_soup(self):
        """Does EnabBaladi.get_soup return a BeautifulSoup object?"""

        soup = self.enabbaladi.get_soup(
            url="https://www.enabbaladi.net/archives/category/online/page/1"
        )
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return dataclass with correct info?"""

        scrape_result = self.enabbaladi.get_news_articles_by_page(page_num=1)

        """Does get_news_articles_by_page return ScrapeResult dataclass?"""
        self.assertTrue(isinstance(scrape_result, ScrapeResult))

        """Does ScrapeResult indicate success and contain an article list?"""
        self.assertTrue(scrape_result.success)
        self.assertTrue(len(scrape_result.article_list) > 1)

    def test_get_full_text_and_date_posted(self):
        """Does get_full_text_and_date_posted return correct data"""

        [date_posted, full_text] = self.enabbaladi.get_full_text_and_date_posted(
            "https://www.enabbaladi.net/archives/651728"
        )

        """Does get_full_text_and_date_posted return correct date_posted?"""
        self.assertEqual(date_posted, "2023-07-23T13:03:36+00:00")

        """Does get_full_text_and_date_posted return correct full_text?"""
        self.assertTrue(type(full_text) == str and len(full_text) > 0)


class HouranFLTestCase(TestCase):
    """Tests for houranfl.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.houranfl = houranfl.HouranFL()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does HouranFL have correct url_template and publication properties?"""

        self.assertEqual(
            self.houranfl.config.url_template,
            "https://www.horanfree.com/page/{page_num}?cat=%2A",
        )
        self.assertEqual(self.houranfl.config.publication, "Houran Free League")
        self.assertEqual(
            self.houranfl.config.should_get_metadata_during_pagination, False
        )

    def test_get_soup(self):
        """Does HouranFL.get_soup return a BeautifulSoup object?"""

        soup = self.houranfl.get_soup(url="https://www.horanfree.com/page/1?cat=%2A")
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return dataclass with correct info?"""

        scrape_result = self.houranfl.get_news_articles_by_page(page_num=1)

        """Does get_news_articles_by_page return ScrapeResult dataclass?"""
        self.assertTrue(isinstance(scrape_result, ScrapeResult))

        """Does get_news_articles_by_page indicate success and contain an article list?"""
        self.assertTrue(scrape_result.success)
        self.assertTrue(len(scrape_result.article_list) > 1)

    def test_get_full_text_and_date_posted(self):
        """Does get_full_text_and_date_posted return the article's text"""

        [date_posted, full_text] = self.houranfl.get_full_text_and_date_posted(
            "https://www.horanfree.com/archives/13818"
        )

        """Does it return correct date_posted?"""
        self.assertEqual(date_posted, "2023-07-19T15:33:21+03:00")

        """Does it return correct full_text?"""
        self.assertTrue(type(full_text) == str and len(full_text) > 0)


class SANATestCase(TestCase):
    """Tests for sana.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.SANA = sana.SANA()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does SANA have correct url_template and publication properties?"""

        self.assertEqual(
            self.SANA.config.url_template,
            "https://sana.sy/?cat=29582&paged={page_num}",
        )
        self.assertEqual(
            self.SANA.config.publication, "SANA (Syrian Arab News Agency)"
        )
        self.assertEqual(self.SANA.config.should_get_metadata_during_pagination, True)

    def test_get_soup(self):
        """Does SANA.get_soup return a BeautifulSoup object?"""

        soup = self.SANA.get_soup(url="https://sana.sy/?cat=29582&paged=1")
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return dataclass with correct info?"""

        scrape_result = self.SANA.get_news_articles_by_page(page_num=1)

        """Does get_news_articles_by_page return ScrapeResult dataclass?"""
        self.assertTrue(isinstance(scrape_result, ScrapeResult))

        """Does get_news_articles_by_page indicate success and contain an article list?"""
        self.assertTrue(scrape_result.success)
        self.assertTrue(len(scrape_result.article_list) > 1)

    def test_get_article_full_text(self):
        """Does get_article_full_text return the article's text"""

        article_text = self.SANA.get_article_full_text("https://sana.sy/?p=1937484")

        self.assertTrue(type(article_text) == str and len(article_text) > 0)

    def test_get_timestamp(self):
        """Does get_timestamp return correct unix timestamp"""

        timestamp = self.SANA.get_timestamp("2023-07-24")

        self.assertTrue(type(timestamp), int)
        self.assertTrue(timestamp == 1690171200)


##### NOTE: Currently failing due to cloudflare issues
# class SDFPressTestCase(TestCase):
#     """Tests for sdfpress.py"""


class Suwayda24TestCase(TestCase):
    """Tests for suwayda24.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.suwayda24 = suwayda24.Suwayda24()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does Suwayda24 have correct url_template and publication properties?"""

        self.assertEqual(
            self.suwayda24.config.url_template,
            "https://suwayda24.com/?cat=%2A&paged={page_num}",
        )

        self.assertEqual(self.suwayda24.config.publication, "Suwayda 24")

        self.assertEqual(
            self.suwayda24.config.should_get_metadata_during_pagination, False
        )

    def test_get_soup(self):
        """Does Suwayda24.get_soup return a BeautifulSoup object?"""

        soup = self.suwayda24.get_soup(url="https://suwayda24.com/?cat=%2A&paged=1")
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return dataclass with correct info?"""

        scrape_result = self.suwayda24.get_news_articles_by_page(page_num=1)

        """Does get_news_articles_by_page return ScrapeResult dataclass?"""
        self.assertTrue(isinstance(scrape_result, ScrapeResult))

        """Does get_news_articles_by_page indicate success and contain an article list?"""
        self.assertTrue(scrape_result.success)
        self.assertTrue(len(scrape_result.article_list) > 1)

    def test_get_full_text_and_date_posted(self):
        """Does get_full_text_and_date_posted return the article's text"""

        [date_posted, full_text] = self.suwayda24.get_full_text_and_date_posted(
            "https://suwayda24.com/?p=21571"
        )

        """Does it return correct date_posted"""
        self.assertEqual(date_posted, "2023-07-21T14:52:25+03:00")

        """Does it return correct full_text?"""
        self.assertTrue(type(full_text) == str and len(full_text) > 0)


class SyriaDirectTestCase(TestCase):
    """Tests for syriadirect.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.syriadirect = syriadirect.SyriaDirect()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does SyriaDirect have correct url_template and publication properties?"""

        self.assertEqual(
            self.syriadirect.config.url_template,
            "https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/{page_num}/?lang=ar",
        )
        self.assertEqual(self.syriadirect.config.publication, "Syria Direct")
        self.assertEqual(
            self.syriadirect.config.should_get_metadata_during_pagination, True
        )

    def test_get_soup(self):
        """Does SyriaDirect.get_soup return a BeautifulSoup object?"""

        soup = self.syriadirect.get_soup(
            url="https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/1/?lang=ar"
        )
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return dataclass with correct info?"""

        scrape_result = self.syriadirect.get_news_articles_by_page(page_num=1)

        """Does get_news_articles_by_page return ScrapeResult dataclass?"""
        self.assertTrue(isinstance(scrape_result, ScrapeResult))

        """Does get_news_articles_by_page indicate success and contain an article list?"""
        self.assertTrue(scrape_result.success)
        self.assertTrue(len(scrape_result.article_list) > 1)

    def test_get_article_full_text(self):
        """Does get_article_full_text return text from article?"""

        article_text = self.syriadirect.get_article_full_text(
            "https://syriadirect.org/%d8%a8%d8%b0%d8%b1%d9%8a%d8%b9%d8%a9-%d8%a7%d9%84%d8%ad%d9%81%d8%a7%d8%b8-%d8%b9%d9%84%d9%89-%d8%a7%d9%84%d8%aa%d8%b1%d8%a7%d8%ab-%d8%b9%d9%85%d9%84%d9%8a%d8%a7%d8%aa-%d8%aa%d8%b1%d9%85%d9%8a%d9%85/?lang=ar"
        )

        self.assertTrue(type(article_text) == str and len(article_text) > 0)
