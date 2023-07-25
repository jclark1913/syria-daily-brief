import os
from unittest import TestCase, mock
from sdb.models import db, Collection, Entry

os.environ["DATABASE_URL"] = "postgresql:///sdb_test"

from sdb.app import app

from sdb.translation import (
    initialize_argostranslate,
    translate_ar_to_en,
    get_translated_entry_title_and_text,
)

db.drop_all()
db.create_all()

class TranslationTestCase(TestCase):
    """Tests for translation.py"""

    def setUp(self):
        """Create test client, add sample data.

        NOTE: It's a lot of setup for just unit tests, but since we feed the
        translation methods a whole entry, we need to create a collection and
        entry here.
        """

        Collection.query.delete()
        Entry.query.delete()

        self.client = app.test_client()

        self.collection = Collection(
            name="Test Collection", description="Test Description"
        )
        db.session.add(self.collection)
        db.session.commit()

        self.collection_id = self.collection.id

        self.entry = Entry(
            title="Test Entry",
            collection_id=self.collection_id,
            publication="Test Publication",
        )

        db.session.add(self.entry)
        db.session.commit()


    def test_initialize_argos_translate(self):
        """Does initialize_argostranslate run without error?"""

        """Should run without throwing error"""
        initialize_argostranslate()

    def test_translate_ar_to_en(self):
        """Does translate_ar_to_en run without error?"""

        with mock.patch("argostranslate.translate.translate") as mocked_translation:
            mocked_translation.return_value = "test"

            """Should run without throwing error"""
            translation = translate_ar_to_en("اختبار")

            """Should return mocked return value"""
            self.assertEqual(translation, "test")

    def test_get_translated_entry_title_and_text(self):
        """Does test_get_translated_entry_title_and_text return translated title and text in list?"""

        with mock.patch("argostranslate.translate.translate") as mocked_translation:
            mocked_translation.return_value = "test"

            """Should run without throwing error"""
            [en_title, en_full_text] = get_translated_entry_title_and_text(self.entry)

            """Should return mocked return value"""
            self.assertEqual(en_title, "test")
            self.assertEqual(en_full_text, "test")
