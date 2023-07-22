from unittest import TestCase, mock
from bs4 import BeautifulSoup

# import every file from scrapers directory

from syriadailybrief.scrapers import base_scraper, dez24


class BaseScraperTestCase(TestCase):
    """Tests for base_scraper.py"""

    def test_is_abstract_class(self):
        """Is BaseScraper an abstract class?"""

        """Should raise TypeError when attempting to instantiate BaseScraper"""
        with self.assertRaises(TypeError):
            base_scraper.Base_Scraper()


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

    # def test_get_news_articles_by_page(self):
    #     """Does get_news_articles_by_page return correct data?"""


