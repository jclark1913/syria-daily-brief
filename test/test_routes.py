import os
from unittest import TestCase, mock
from unittest.mock import patch
from sdb.models import db, Collection, Entry

os.environ["DATABASE_URL"] = "postgresql:///sdb_test"

from sdb.app import app

db.drop_all()
db.create_all()


class APICollectionsRoutesTestCase(TestCase):
    """Tests for /api/collections routes"""

    def setUp(self):
        """Create test client, add sample data"""

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
            collection_id=self.collection.id,
            publication="Test Publication",
        )

        db.session.add(self.entry)
        db.session.commit()

        self.entry_id = self.entry.id

    def tearDown(self):
        db.session.rollback()

    def test_get_collections(self):
        """Does GET /api/collections return a list of collections?"""

        response = self.client.get("/api/collections")
        data = response.json

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return a list of collections w/ correct data"""
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Collection")

    def test_create_collection(self):
        """Does POST /api/collections add a new collection to the db?"""

        input = {"name": "New Collection", "description": "New Description"}

        response = self.client.post("/api/collections", json=input)
        data = response.json
        new_collection = Collection.query.filter_by(name="New Collection").first()

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return JSON of newly added collection"""
        self.assertEqual(data["created"]["name"], "New Collection")
        self.assertEqual(data["created"]["description"], "New Description")

        """Should add new collection to db"""
        self.assertEqual(Collection.query.count(), 2)
        self.assertTrue(new_collection.name == "New Collection")

    def test_create_collection_invalid(self):
        """Does POST /api/collections w/ invalid data return error?"""

        input = {"wrong_name": "New Collection"}

        response = self.client.post("/api/collections", json=input)
        data = response.json

        """Should return 400 status code"""
        self.assertEqual(response.status_code, 400)

        """Should return error message"""
        self.assertEqual(data["errors"]["name"][0], "Missing data for required field.")
        self.assertEqual(data["errors"]["wrong_name"][0], "Unknown field.")

    def test_get_collection(self):
        """Does GET /api/collections/<collection_id> return a collection?"""

        response = self.client.get(f"/api/collections/{self.collection_id}")
        data = response.json

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return JSON of collection"""
        self.assertEqual(data["name"], "Test Collection")
        self.assertEqual(data["description"], "Test Description")

    def test_get_collection_invalid(self):
        """Does GET /api/collections/<collection_id> w/ return error if not found?"""

        response = self.client.get("/api/collections/1000")

        """Should return 404 status code"""
        self.assertEqual(response.status_code, 404)

    def test_update_collection(self):
        """Does POST /api/collections/<collection_id> update a collection?"""

        input = {"name": "Updated Collection", "description": "Updated Description"}

        response = self.client.post(
            f"/api/collections/{self.collection_id}", json=input
        )
        data = response.json

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return JSON of updated collection"""
        self.assertEqual(data["Collection updated"]["name"], "Updated Collection")
        self.assertEqual(
            data["Collection updated"]["description"], "Updated Description"
        )

        """Should update collection in db"""
        self.assertEqual(Collection.query.count(), 1)
        self.assertTrue(Collection.query.first().name == "Updated Collection")

    def test_update_collection_invalid(self):
        """Does POST /api/collections/<collection_id> w/ invalid data return error?"""

        input = {"wrong_name": "Updated Collection"}

        response = self.client.post(
            f"/api/collections/{self.collection_id}", json=input
        )

        data = response.json

        """Should return 400 status code"""
        self.assertEqual(response.status_code, 400)

        """Should return error message"""
        self.assertEqual(data["errors"]["wrong_name"][0], "Unknown field.")

    def test_delete_collection(self):
        """Does DELETE /api/collections/<collection_id> delete a collection?"""

        response = self.client.delete(f"/api/collections/{self.collection_id}")

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should delete collection from db"""
        self.assertEqual(Collection.query.count(), 0)

    def test_delete_collection_invalid(self):
        """Does DELETE /api/collections/<collection_id> w/ invalid id return error?"""

        response = self.client.delete("/api/collections/1000")

        """Should return 404 status code"""
        self.assertEqual(response.status_code, 404)

    def test_get_entries_from_collection(self):
        """Does GET /api/collections/<collection_id>/entries return a list of entries?"""

        response = self.client.get(f"/api/collections/{self.collection_id}/entries")
        data = response.json

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return a list of entries w/ correct data"""
        self.assertEqual(len(data), 1)
        self.assertEqual(data["Test Collection"][0]["title"], "Test Entry")


class APIEntriesRoutesTestCase(TestCase):
    """Tests for /api/entries routes"""

    def setUp(self):
        """Create test client, add sample data"""

        Collection.query.delete()
        Entry.query.delete()

        self.client = app.test_client()

        self.collection = Collection(
            name="Test Collection", description="Test Description"
        )

        self.entry = Entry(
            title="Test Entry",
            collection_id=self.collection.id,
            publication="Test Publication",
        )

        db.session.add(self.collection)
        db.session.add(self.entry)
        db.session.commit()

        self.collection_id = self.collection.id
        self.entry_id = self.entry.id

    def tearDown(self):
        db.session.rollback()

    def test_get_single_entry(self):
        """Does GET /api/entries/<entry_id> return the correct entry?"""

        response = self.client.get(f"/api/entries/{self.entry_id}")
        data = response.json

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return JSON of entry"""
        self.assertEqual(data["title"], "Test Entry")
        self.assertEqual(data["publication"], "Test Publication")

    def test_get_single_entry_invalid(self):
        """Does GET /api/entries/<entry_id> return a 404 if no entry found?"""

        response = self.client.get("/api/entries/1000")

        """Should return 404 status code"""
        self.assertEqual(response.status_code, 404)

    def test_edit_single_entry(self):
        """Does POST /api/entries/<int:entry_id> update an entry?"""

        response = self.client.post(
            f"/api/entries/{self.entry_id}",
            json={"title": "Updated Entry", "publication": "Updated Publication"},
        )

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should update entry in db"""
        self.assertEqual(Entry.query.count(), 1)
        self.assertTrue(Entry.query.first().title == "Updated Entry")
        self.assertTrue(Entry.query.first().publication == "Updated Publication")

    def test_edit_single_entry_invalid(self):
        """Does POST /api/entries/<int:entry_id> w/ invalid data return error?"""

        response = self.client.post(
            f"/api/entries/{self.entry_id}",
            json={"wrong_title": "Updated Entry", "publication": "Updated Publication"},
        )
        data = response.json

        """Should return 400 status code"""
        self.assertEqual(response.status_code, 400)

        """Should return error message"""
        self.assertEqual(data["errors"]["wrong_title"][0], "Unknown field.")

    def test_delete_single_entry(self):
        """Does DELETE /api/entries/<int:entry_id> delete an entry?"""

        response = self.client.delete(f"/api/entries/{self.entry_id}")
        data = response.json

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should delete entry from db"""
        self.assertEqual(Entry.query.count(), 0)

        """Should return success message"""
        self.assertEqual(data["Deleted entry"], self.entry_id)

    def test_delete_single_entry_invalid(self):
        """Does DELETE /api/entries/<int:entry_id> w/ invalid id return error?"""

        response = self.client.delete(f"/api/entries/1000")

        """Should return 404 status code"""
        self.assertEqual(response.status_code, 404)


class APITranslateTestCase(TestCase):
    """Tests for /api/translate"""

    def setUp(self):
        """Create test client, add sample data"""

        Collection.query.delete()
        Entry.query.delete()

        self.client = app.test_client()

        self.collection = Collection(
            name="Test Collection", description="Test Description"
        )

        db.session.add(self.collection)
        db.session.commit()

        self.collection_id = self.collection.id

        self.entry1 = Entry(
            title="عنوان المقالة الاولى",
            collection_id=self.collection.id,
            publication="Test Publication",
            full_text="هذا النص الكامل للمقالة الأولى في اللغة العربية",
        )

        self.entry2 = Entry(
            title="عنوان المقالة الثانية",
            collection_id=self.collection.id,
            publication="Test Publication",
            full_text="هذا النص الكامل للمقالة الثانية في اللغة العربية",
        )

        db.session.add(self.entry1)
        db.session.add(self.entry2)
        db.session.commit()

        self.entry1_id = self.entry1.id
        self.entry2_id = self.entry2.id

    def tearDown(self):
        db.session

    # NOTE: In the future maybe consider using mock.patch decorators for cleaner code.
    def test_translate_entries(self):
        """Does POST /api/translate translate multiple entries?"""

        with mock.patch(
            "sdb.translation.get_translated_entry_title_and_text",
            mock.Mock(return_value=["English Title", "English Text"]),
        ), mock.patch(
            "sdb.translation.initialize_argostranslate", mock.Mock(return_value=None)
        ):
            response = self.client.post(
                "/api/translate",
                json={"entry_ids": [self.entry1_id, self.entry2_id]},
            )
            data = response.json

            """Should return 200 status code"""
            self.assertEqual(response.status_code, 200)

            """Should return JSON of translated entries"""
            self.assertEqual(len(data["Translated"]), 2)
            self.assertEqual(data["Translated"][0]["title_translated"], "English Title")
            self.assertEqual(
                data["Translated"][1]["full_text_translated"], "English Text"
            )

            """Should update the database"""
            self.assertEqual(Entry.query.count(), 2)
            self.assertEqual(Entry.query.first().title_translated, "English Title")
            self.assertEqual(Entry.query.first().full_text_translated, "English Text")
            self.assertEqual(
                Entry.query.get(self.entry2_id).title_translated, "English Title"
            )
            self.assertEqual(
                Entry.query.get(self.entry2_id).full_text_translated, "English Text"
            )

    def test_translate_entries_not_found(self):
        """Does POST /api/translate w/ invalid data (nonexistant entry) return error message?"""

        with mock.patch(
            "sdb.translation.get_translated_entry_title_and_text",
            mock.Mock(return_value=["English Title", "English Text"]),
        ), mock.patch(
            "sdb.translation.initialize_argostranslate", mock.Mock(return_value=None)
        ):
            response = self.client.post("/api/translate", json={"entry_ids": [1000]})
            data = response.json

            """Should return 400 status code"""
            self.assertEqual(response.status_code, 400)

            """Should return error message"""
            self.assertEqual(data["error"], "No entries found.")

    def test_translate_entries_invalid(self):
        """Does POST /api/translate w/ invalid JSON data return ValidationError?"""

        with mock.patch(
            "sdb.translation.get_translated_entry_title_and_text",
            mock.Mock(return_value=["English Title", "English Text"]),
        ), mock.patch(
            "sdb.translation.initialize_argostranslate", mock.Mock(return_value=None)
        ):
            response = self.client.post(
                "/api/translate",
                json={
                    "entry_ids": [self.entry1_id, self.entry2_id, 1000],
                    "invalid": "invalid",
                },
            )

            data = response.json

            """Should return 400 status code"""
            self.assertEqual(response.status_code, 400)

            """Should return errors"""
            self.assertEqual(data["errors"]["invalid"][0], "Unknown field.")

            """Should not update the database"""
            self.assertFalse(Entry.query.get(self.entry1_id).title_translated)
            self.assertFalse(Entry.query.get(self.entry2_id).title_translated)


class APISummarizeTestCase(TestCase):
    """Tests for /api/summarize"""

    def setUp(self):
        """Setup test client, add sample data"""

        Collection.query.delete()
        Entry.query.delete()

        self.client = app.test_client()

        self.collection = Collection(
            name="Test Collection", description="Test Description"
        )

        db.session.add(self.collection)
        db.session.commit()

        self.collection_id = self.collection.id

        self.entry1 = Entry(
            title="عنوان المقالة الاولى",
            collection_id=self.collection.id,
            publication="Test Publication",
            full_text="هذا النص الكامل للمقالة الأولى في اللغة العربية",
        )

        self.entry2 = Entry(
            title="عنوان المقالة الثانية",
            collection_id=self.collection.id,
            publication="Test Publication",
            full_text="هذا النص الكامل للمقالة الثانية في اللغة العربية",
        )

        db.session.add(self.entry1)
        db.session.add(self.entry2)
        db.session.commit()

        self.entry1_id = self.entry1.id
        self.entry2_id = self.entry2.id

    @patch("os.getenv", return_value="test")
    def test_summarize_entries(self, mock_getenv):
        """Does POST /api/summarize return summarize multiple entries and update the database?"""

        with mock.patch(
            "sdb.ai_utils.get_ai_summary_for_arabic_text",
            mock.Mock(return_value="Summarized Text"),
        ):
            response = self.client.post(
                "/api/summarize",
                json={"entry_ids": [self.entry1_id, self.entry2_id]},
            )

            data = response.json

            """Should return 200 status code"""
            self.assertEqual(response.status_code, 200)

            """Should return JSON of summarized entries"""
            self.assertEqual(len(data["Summarized"]), 2)
            self.assertEqual(data["Summarized"][0]["ai_summary"], "Summarized Text")
            self.assertEqual(data["Summarized"][1]["ai_summary"], "Summarized Text")

            """Should update the database"""
            self.assertEqual(Entry.query.count(), 2)
            self.assertEqual(Entry.query.first().ai_summary, "Summarized Text")
            self.assertEqual(
                Entry.query.get(self.entry2_id).ai_summary, "Summarized Text"
            )

    """NOTE: This mocking approach is interesting. In order to get this working,
    I did have to make sure that openai_api_key was defined in the route rather
    than at the top of app.py. I don't think this is an issue, but I should do
    some more research on this."""

    @patch("os.getenv")
    def test_summarize_entries_no_key(self, mock_getenv):
        """Should return error if api key not found"""

        def side_effect(arg):
            if arg == "OPENAI_API_KEY":
                return None
            else:
                return os.environ.get(arg)

        mock_getenv.side_effect = side_effect

        with mock.patch(
            "sdb.ai_utils.get_ai_summary_for_arabic_text",
            mock.Mock(return_value="Summarized Text"),
        ):
            response = self.client.post(
                "/api/summarize",
                json={"entry_ids": [self.entry1_id, self.entry2_id]},
            )

            data = response.json

            """Should return 400 status code"""
            self.assertEqual(response.status_code, 400)

            """Should return error message"""
            self.assertEqual(data["error"], "No OpenAI API key found")

            """Should not update the database"""
            self.assertEqual(Entry.query.count(), 2)
            self.assertEqual(Entry.query.first().ai_summary, None)
            self.assertEqual(Entry.query.get(self.entry2_id).ai_summary, None)

    def test_summarize_entries_no_entries(self):
        """Should return error if no entries given"""

        with mock.patch(
            "sdb.ai_utils.get_ai_summary_for_arabic_text",
            mock.Mock(return_value="Summarized Text"),
        ):
            response = self.client.post("/api/summarize", json={"entry_ids": []})

            data = response.json

            """Should return 400 status code"""
            self.assertEqual(response.status_code, 400)

            """Should return error message"""
            self.assertEqual(data["error"], "No entries found.")

            """Should not update the database"""
            self.assertEqual(Entry.query.count(), 2)
            self.assertEqual(Entry.query.first().ai_summary, None)
            self.assertEqual(Entry.query.get(self.entry2_id).ai_summary, None)

    def test_summarize_entries_invalid_entry(self):
        """Should return error if invalid entry given"""

        with mock.patch(
            "sdb.ai_utils.get_ai_summary_for_arabic_text",
            mock.Mock(return_value="Summarized Text"),
        ):
            response = self.client.post(
                "/api/summarize",
                json={"entry_ids": [self.entry1_id], "invalid": "invalid"},
            )

            data = response.json

            """Should return 400 status code"""
            self.assertEqual(response.status_code, 400)

            """Should return error message"""
            self.assertEqual(data["errors"]["invalid"][0], "Unknown field.")

            """Should not update the database"""
            self.assertEqual(Entry.query.count(), 2)
            self.assertEqual(Entry.query.first().ai_summary, None)
            self.assertEqual(Entry.query.get(self.entry2_id).ai_summary, None)


class APIMigrateEntriesTestCase(TestCase):
    """Tests for /api/migrate"""

    def setUp(self):
        """Create test client, add sample data"""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.collection1 = Collection(
            name="Test Collection 1", description="Test Description 1"
        )

        db.session.add(self.collection1)
        db.session.commit()

        self.collection1_id = self.collection1.id

        self.collection2 = Collection(
            name="Test Collection 2", description="Test Description 2"
        )

        db.session.add(self.collection2)
        db.session.commit()

        self.collection2_id = self.collection2.id

        self.entry1 = Entry(
            title="عنوان المقالة الاولى",
            collection_id=self.collection1_id,
            publication="Test Publication",
            full_text="هذا النص الكامل للمقالة الأولى في اللغة العربية",
        )

        self.entry2 = Entry(
            title="عنوان المقالة الثانية",
            collection_id=self.collection1_id,
            publication="Test Publication",
            full_text="هذا النص الكامل للمقالة الثانية في اللغة العربية",
        )

        db.session.add(self.entry1)
        db.session.add(self.entry2)
        db.session.commit()

        self.entry1_id = self.entry1.id
        self.entry2_id = self.entry2.id

    def tearDown(self):
        db.session.rollback()

    def test_migrate_entries_copy(self):
        """Does POST /api/migrate copy entries to new collection?"""

        response = self.client.post(
            "/api/migrate_entries",
            json={
                "entry_ids": [self.entry1_id, self.entry2_id],
                "origin_collection_id": self.collection1_id,
                "destination_collection_id": self.collection2_id,
            },
        )

        data = response.json

        origin_collection = Collection.query.get(self.collection1_id)
        destination_collection = Collection.query.get(self.collection2_id)

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return success message"""
        self.assertEqual(
            data["message"],
            "2 entries added to Test Collection 2 from Test Collection 1.",
        )

        """Should copy entries to destination collection w/o deleting them"""
        self.assertEqual(Entry.query.count(), 4)
        self.assertEqual(len(origin_collection.entries), 2)
        self.assertEqual(len(destination_collection.entries), 2)

    def test_migrate_entries_delete(self):
        """Does POST /api/migrate_entries move entries to new collection and delete from old?"""

        response = self.client.post(
            "/api/migrate_entries",
            json={
                "entry_ids": [self.entry1_id, self.entry2_id],
                "origin_collection_id": self.collection1_id,
                "destination_collection_id": self.collection2_id,
                "delete_on_move": True,
            },
        )

        data = response.json

        origin_collection = Collection.query.get(self.collection1_id)
        destination_collection = Collection.query.get(self.collection2_id)

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return success message"""
        self.assertEqual(
            data["message"],
            "2 entries added to Test Collection 2 from Test Collection 1. 2 entries deleted from Test Collection 1.",
        )

        """Should move entries to destination collection and delete from origin collection"""
        self.assertEqual(Entry.query.count(), 2)
        self.assertEqual(len(origin_collection.entries), 0)
        self.assertEqual(len(destination_collection.entries), 2)

    def test_migrate_entries_no_entries(self):
        """Does POST /api/migrate_entries return error if no entries given?"""

        response = self.client.post(
            "/api/migrate_entries",
            json={
                "entry_ids": [],
                "origin_collection_id": self.collection1_id,
                "destination_collection_id": self.collection2_id,
            },
        )

        data = response.json

        """Should return 400 status code"""
        self.assertEqual(response.status_code, 400)

        """Should return error message"""
        self.assertEqual(data["error"], "No entries found.")

        """Should not update the database"""
        self.assertEqual(Entry.query.count(), 2)
        self.assertEqual(len(self.collection1.entries), 2)
        self.assertEqual(len(self.collection2.entries), 0)

