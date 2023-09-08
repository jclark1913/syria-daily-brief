import os
from enum import Enum
from unittest import TestCase
from unittest.mock import Mock, patch

os.environ["DATABASE_URL"] = "postgresql:///sdb_test"

from sdb.app import app
from sdb.controller import (
    run_selected_scrapers,
    add_entries_to_db,
    ScraperMap,
    generate_excel_from_collection,
    get_available_scrapers,
)

from sdb.scrapers import dez24, sana

from sdb.models import db, Collection, Entry
from sdb.scrapers.scrape_result import ScrapeResult

db.drop_all()
db.create_all()


class ControllerTestCase(TestCase):
    """Tests for controller.py"""

    def setUp(self):
        """Create test client, add sample data."""

        Collection.query.delete()
        Entry.query.delete()

        collection = Collection(name="Test Collection")

        db.session.add(collection)
        db.session.commit()

        self.collection_id = collection.id

        self.entry = Entry(
            title="Test Entry",
            collection_id=self.collection_id,
            publication="Test Publication",
        )

        db.session.add(self.entry)
        db.session.commit()

        self.entry_id = self.entry.id

    def tearDown(self):
        db.session.rollback()

    def test_ScraperMap(self):
        """Does ScraperMap return correct scraper instances?"""

        """Calling the enum value should return an instance of the scraper class"""
        for enum in ScraperMap:
            self.assertIsInstance(enum.value(), enum.value)

    def test_get_available_scrapers(self):
        """Does get_available_scrapers return list of dictionaries for each available scraper?"""

        scraper_list = get_available_scrapers(map=ScraperMap)

        expected_scraper_list = [
            {"value": scraper.value, "label": scraper.lable} for scraper in ScraperMap
        ]

        """Should return correct number of scrapers"""
        self.assertEqual(len(scraper_list), len(ScraperMap))

        """Should return correct scraper names"""
        self.assertListEqual(scraper_list, expected_scraper_list)

    def test_add_entries_to_db(self):
        """Does add_entries_to_db add given entries to db?"""

        entry_2_dict = {
            "title": "Test Entry 2",
            "publication": "Test Publication",
            "link": "Test Link",
            "date_posted": 123456789,
            "full_text": "Test Full Text",
        }

        entry_3_dict = {
            "title": "Test Entry 3",
            "publication": "Test Publication",
            "link": "Test Link",
            "date_posted": 123456789,
            "full_text": "Test Full Text",
        }

        entries = [entry_2_dict, entry_3_dict]

        add_entries_to_db(entries=entries, collection_id=self.collection_id)

        """Should put entries in db"""
        self.assertEqual(len(Entry.query.all()), 3)

        entry_2 = Entry.query.filter_by(title="Test Entry 2").first()
        entry_3 = Entry.query.filter_by(title="Test Entry 3").first()

        """Should put entries in correct collection"""
        self.assertIn(entry_2, Collection.query.get(self.collection_id).entries)
        self.assertIn(entry_3, Collection.query.get(self.collection_id).entries)

        """Should input correct data"""
        self.assertEqual(entry_2.title, "Test Entry 2")
        self.assertEqual(entry_2.publication, "Test Publication")
        self.assertEqual(entry_2.full_text, "Test Full Text")
        self.assertEqual(entry_2.date_posted, "123456789")
        self.assertEqual(entry_2.link, "Test Link")

    @patch("sdb.scrapers.sana.SANA.get_data")
    @patch("sdb.scrapers.dez24.DEZ24.get_data")
    def test_run_selected_scrapers(self, mock_sana, mock_dez24):
        """Does run_selected_scrapers gather correct data and update db?"""

        scrape_result = ScrapeResult()
        scrape_result.article_list = [
            {
                "title": "Scraped Entry 1",
                "publication": "Test Publication",
                "link": "Test Link",
                "date_posted": 123456789,
                "full_text": "Test Full Text",
            },
            {
                "title": "Scraped Entry 2",
                "publication": "Test Publication",
                "link": "Test Link",
                "date_posted": 123456789,
                "full_text": "Test Full Text",
            },
        ]
        scrape_result.success = True

        mock_sana.return_value = scrape_result
        mock_dez24.return_value = scrape_result

        selected_scrapers = [ScraperMap.SANA, ScraperMap.DEZ24]

        [dataclasses, errors] = run_selected_scrapers(
            selections=selected_scrapers,
            stop_timestamp=0,
            collection_id=self.collection_id,
        )

        test_entry = Entry.query.filter_by(title="Scraped Entry 1").first()

        """Should return correct number of dataclasses w/ correct info"""
        for dataclass in dataclasses:
            self.assertIsInstance(dataclass, ScrapeResult)
            self.assertTrue(dataclass.success)
        self.assertEqual(len(dataclasses), 2)

        """Should return no errors"""
        self.assertEqual(errors, [])

        """Should add entries to db"""
        self.assertEqual(len(Entry.query.all()), 5)

        """Should add entries to correct collection"""
        self.assertEqual(len(Collection.query.get(self.collection_id).entries), 5)

        """Should add correct data to db"""
        self.assertEqual(test_entry.collection_id, self.collection_id)
        self.assertEqual(test_entry.publication, "Test Publication")
        self.assertEqual(test_entry.link, "Test Link")
        self.assertEqual(test_entry.date_posted, "123456789")
        self.assertEqual(test_entry.full_text, "Test Full Text")

    @patch("sdb.scrapers.sana.SANA.get_data")
    @patch("sdb.scrapers.dez24.DEZ24.get_data")
    def test_run_selected_scrapers_errorful(self, mock_sana, mock_dez24):
        """Does run_selected_scrapers return errors when errors occur?"""

        scrape_result = ScrapeResult()
        scrape_result.article_list = []
        scrape_result.success = False

        mock_sana.return_value = scrape_result
        mock_dez24.return_value = scrape_result

        selected_scrapers = [ScraperMap.SANA, ScraperMap.DEZ24]

        [dataclasses, errors] = run_selected_scrapers(
            selections=selected_scrapers,
            stop_timestamp=0,
            collection_id=self.collection_id,
        )

        """Should return correct number of dataclasses w/ correct info"""
        for dataclass in dataclasses:
            self.assertIsInstance(dataclass, ScrapeResult)
            self.assertFalse(dataclass.success)
        self.assertEqual(len(dataclasses), 2)

        """Should return correct number of errors"""
        self.assertEqual(len(errors), 2)

        """Should add no entries to db"""
        self.assertEqual(len(Entry.query.all()), 1)

    def test_get_available_scrapers(self):
        """Does get_available_scrapers return correct scrapers?"""

        class test_map(Enum):
            SANA = sana.SANA
            DEZ24 = dez24.DEZ24

        scraper_list = get_available_scrapers(map=test_map)

        """Should return correct number of scrapers"""
        self.assertEqual(len(scraper_list), 2)

        """Should return correct scraper names"""
        self.assertEqual(
            scraper_list[0],
            {"value": "SANA", "label": "SANA (Syrian Arab News Agency)"},
        )
        self.assertEqual(scraper_list[1], {"value": "DEZ24", "label": "Deir Ezzor 24"})

    # TODO: Test generate_excel_from_collection (possibly with Pandas snapshot test)
    # def test_generate_excel_from_collection(self):
    #     """Does generate_excel_from_collection generate correct excel file?"""
