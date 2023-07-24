from unittest import TestCase, mock
from bs4 import BeautifulSoup

# import every file from scrapers directory

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
            base_scraper.Base_Scraper()

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

    def test_reached_time_limit_recurse(self):
        """Does reached_time_limit_recurse return correct boolean?"""

        test_scraper = dez24.DEZ24()

        """Should return True if current_timestamp is greater than stop_timestamp"""
        self.assertTrue(
            test_scraper.reached_time_limit_recurse(
                stop_timestamp=1, current_timestamp=1000
            )
        )

        """Should return True if current_timestamp is equal to stop_timestamp"""
        self.assertTrue(test_scraper.reached_time_limit_recurse(1, 1))

        """Should return false if current_timestamp is less than stop_timestamp"""
        self.assertFalse(test_scraper.reached_time_limit_recurse(1000, 1))

        """Shoulre return False if stop_timestamp is not passed into method"""
        self.assertFalse(test_scraper.reached_time_limit_recurse(current_timestamp=1000))


class DEZ24TestCase(TestCase):
    """Test for dez24.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.dez24 = dez24.DEZ24()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does DEZ24 have correct url_template and publication properties?"""

        self.assertEqual(
            self.dez24.url_template,
            "https://deirezzor24.net/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1/page/{page_num}/",
        )
        self.assertEqual(self.dez24.publication, "Deir Ezzor 24")

    def test_get_soup(self):
        """Does DEZ24.get_soup return a BeautifulSoup object?"""

        soup = self.dez24.get_soup(
            url="https://deirezzor24.net/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1/page/1/"
        )
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return list of articles?"""

        article_list = self.dez24.get_news_articles_by_page(page_num=1)
        self.assertEqual(len(article_list), 10)

    def test_get_article_text_and_last_updated(self):
        """Does get_article_text_and_last_updated return correct data?"""

        article = self.dez24.get_article_text_and_last_updated(
            "https://deirezzor24.net/%d8%b9%d9%86%d8%a7%d8%b5%d8%b1-%d8%a7%d9%84%d9%81%d9%8a%d9%84%d9%82-%d8%a7%d9%84%d8%ae%d8%a7%d9%85%d8%b3-%d8%a8%d8%af%d9%8a%d8%b1%d8%a7%d9%84%d8%b2%d9%88%d8%b1-%d9%8a%d9%87%d8%af%d8%af%d9%88%d9%86/"
        )
        self.assertTrue(
            type(article["article_text"]) == str and len(article["article_text"]) > 0
        )
        self.assertTrue(
            type(article["last_updated"]) == str and len(article["last_updated"]) > 0
        )


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
            self.enabbaladi.url_template,
            "https://www.enabbaladi.net/archives/category/online/page/{page_num}",
        )
        self.assertEqual(self.enabbaladi.publication, "Enab Baladi")

    def test_get_soup(self):
        """Does EnabBaladi.get_soup return a BeautifulSoup object?"""

        soup = self.enabbaladi.get_soup(
            url="https://www.enabbaladi.net/archives/category/online/page/1"
        )
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return list of articles?"""

        article_list = self.enabbaladi.get_news_articles_by_page(page_num=1)
        self.assertTrue(len(article_list) > 1)

    def test_get_article_text(self):
        """Does get_article_text return correct data"""

        article_text = self.enabbaladi.get_article_text(
            "https://www.enabbaladi.net/archives/651728"
        )
        self.assertTrue(type(article_text) == str and len(article_text) > 0)


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
            self.houranfl.url_template,
            "https://www.horanfree.com/page/{page_num}?cat=%2A",
        )
        self.assertEqual(self.houranfl.publication, "Houran Free League")

    def test_get_soup(self):
        """Does HouranFL.get_soup return a BeautifulSoup object?"""

        soup = self.houranfl.get_soup(url="https://www.horanfree.com/page/1?cat=%2A")
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return list of articles?"""

        article_list = self.houranfl.get_news_articles_by_page(page_num=1)
        self.assertTrue(len(article_list) > 1)

    def test_get_article_text(self):
        """Does get-article_text return the article's text"""

        article_text = self.houranfl.get_article_text(
            "https://www.horanfree.com/archives/13818"
        )

        self.assertTrue(type(article_text) == str and len(article_text) > 0)

    def test_get_timestamp_from_arabic_latin_date_HFL(self):
        """Does get_timestamp_from_arabic_latin_date_HFL return correct timestamp?"""

        timestamp = self.houranfl.get_timestamp_from_arabic_latin_date_HFL(
            "23 يوليو، 2023"
        )

        self.assertTrue(type(timestamp), int)
        self.assertTrue(timestamp == 1690084800)


class SanaTestCase(TestCase):
    """Tests for sana.py"""

    def setUp(self):
        """Create test client, add sample data."""

        self.SANA = sana.SANA()

    def tearDown(self):
        pass

    def test_properties(self):
        """Does SANA have correct url_template and publication properties?"""

        self.assertEqual(
            self.SANA.url_template,
            "https://sana.sy/?cat=29582&paged={page_num}",
        )
        self.assertEqual(self.SANA.publication, "SANA (Syrian Arab News Network)")

    def test_get_soup(self):
        """Does SANA.get_soup return a BeautifulSoup object?"""

        soup = self.SANA.get_soup(url="https://sana.sy/?cat=29582&paged=1")
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return list of articles?"""

        article_list = self.SANA.get_news_articles_by_page(page_num=1)
        self.assertTrue(len(article_list) > 1)

    def test_get_article_text(self):
        """Does get_article_text return the article's text"""

        article_text = self.SANA.get_article_text("https://sana.sy/?p=1937484")

        self.assertTrue(type(article_text) == str and len(article_text) > 0)

    def test_get_timestamp_SANA(self):
        """Does get_timestamp return correct unix timestamp"""

        timestamp = self.SANA.get_timestamp_SANA("2023-07-24")

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
            self.suwayda24.url_template,
            "https://suwayda24.com/?cat=%2A&paged={page_num}",
        )

        self.assertEqual(self.suwayda24.publication, "Suwayda 24")

    def test_get_soup(self):
        """Does Suwayda24.get_soup return a BeautifulSoup object?"""

        soup = self.suwayda24.get_soup(url="https://suwayda24.com/?cat=%2A&paged=1")
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return list of articles?"""

        article_list = self.suwayda24.get_news_articles_by_page(page_num=1)
        self.assertTrue(len(article_list) > 1)

    def test_get_article_text(self):
        """Does get_article_text return the article's text"""

        article_text = self.suwayda24.get_article_text("https://suwayda24.com/?p=21571")

        self.assertTrue(type(article_text) == str and len(article_text) > 0)

    def test_get_s24_eng_timestamp(self):
        """Does get_s24_eng_timestamp return correct unix timestamp"""

        timestamp = self.suwayda24.get_s24_eng_timestamp("07/24/2023")

        self.assertTrue(type(timestamp), int)
        self.assertTrue(timestamp == 1690171200)


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
            self.syriadirect.url_template,
            "https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/{page_num}/?lang=ar",
        )
        self.assertEqual(self.syriadirect.publication, "Syria Direct")

    def test_get_soup(self):
        """Does SyriaDirect.get_soup return a BeautifulSoup object?"""

        soup = self.syriadirect.get_soup(
            url="https://syriadirect.org/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1/page/1/?lang=ar"
        )
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_news_articles_by_page(self):
        """Does get_news_articles_by_page return list of articles?"""

        article_list = self.syriadirect.get_news_articles_by_page(page_num=1)
        self.assertTrue(len(article_list) > 1)

    def test_get_article_text(self):
        """Does get_article_text return text from article?"""

        article_text = self.syriadirect.get_article_text(
            "https://syriadirect.org/%d8%a8%d8%b0%d8%b1%d9%8a%d8%b9%d8%a9-%d8%a7%d9%84%d8%ad%d9%81%d8%a7%d8%b8-%d8%b9%d9%84%d9%89-%d8%a7%d9%84%d8%aa%d8%b1%d8%a7%d8%ab-%d8%b9%d9%85%d9%84%d9%8a%d8%a7%d8%aa-%d8%aa%d8%b1%d9%85%d9%8a%d9%85/?lang=ar"
        )

        self.assertTrue(type(article_text) == str and len(article_text) > 0)

    def test_get_timestamp(self):
        """Does get_timestamp return proper timestamp?"""

        timestamp = self.syriadirect.get_timestamp("2023-07-24T18:37:07.605")

        self.assertTrue(timestamp == 1690238227)
