import os
from unittest import TestCase, mock
from sdb.models import db, Collection, Entry

os.environ["DATABASE_URL"] = "postgresql:///sdb_test"

from sdb.app import app

db.drop_all()
db.create_all()


class APICollectionsRoutesTestCase(TestCase):
    """Tests for /api/collections routes"""

    def setUp(self):
        """Create test client, add sample data"""

        print(os.environ["DATABASE_URL"])

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

        """Should return 200 status code"""
        self.assertEqual(response.status_code, 200)

        """Should return JSON of newly added collection"""
        self.assertEqual(data["created"]["name"], "New Collection")
        self.assertEqual(data["created"]["description"], "New Description")

        """Should add new collection to db"""
        self.assertEqual(Collection.query.count(), 2)
        self.assertEqual(Collection.query.get(2).name, "New Collection")

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
        print(data)
        print(data["Test Collection"])
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
        pass

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


class APITranslateRoutesTestCase(TestCase):
    """Tests for /api/translate"""

    def setUp(self):
        """Create test client, add sample data"""

        print(os.environ["DATABASE_URL"])

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
        pass

    # NOTE: In the future maybe consider using mock.patch decorators for cleaner code.
    def test_translate_entries(self):
        """Does POST /api/translate translate multiple entries?"""

        with mock.patch(
            "argostranslate.translate.translate",
            mock.Mock(return_value="English translation"),
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
            self.assertEqual(
                data["Translated"][0]["title_translated"], "English translation"
            )
            self.assertEqual(
                data["Translated"][1]["full_text_translated"], "English translation"
            )

    def test_translate_entries_invalid(self):
        """Does POST /api/translate w/ invalid data (nonexistant entry) return empty array?"""

        with mock.patch(
            "argostranslate.translate.translate",
            mock.Mock(return_value="English translation"),
        ), mock.patch(
            "sdb.translation.initialize_argostranslate", mock.Mock(return_value=None)
        ):

            response = self.client.post("/api/translate", json={"entry_ids": [1000]})
            data = response.json

            """Should return 400 status code"""
            self.assertEqual(response.status_code, 200)

            """Should return empty array"""
            self.assertEqual(data["Translated"], [])

