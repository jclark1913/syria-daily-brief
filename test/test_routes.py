import os
from unittest import TestCase, mock
from sdb.app import app
from sdb.models import db, Collection, Entry

os.environ["DATABASE_URL"] = "postgresql:///sdb_test"

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

        self.entry = Entry(
            title="Test Entry",
            collection_id=self.collection.id,
            publication="Test Publication",
        )

        db.session.add(self.collection)
        db.session.commit()

        self.collection_id = self.collection.id
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
        data = response.json

        """Should return 404 status code"""
        self.assertEqual(response.status_code, 404)

    # def test_update_collection(self):
    #     """Does POST /api/collections/<collection_id> update a collection?"""

    #     input = {"name": "Updated Collection", "description": "Updated Description"}

    #     response = self.client.post(
    #         f"/api/collections/{self.collection_id}", json=input
    #     )
    #     data = response.json

    #     """Should return 200 status code"""
    #     self.assertEqual(response.status_code, 200)

    #     """Should return JSON of updated collection"""
    #     self.assertEqual(data["updated"]["name"], "Updated Collection")
    #     self.assertEqual(data["updated"]["description"], "Updated Description")

    #     """Should update collection in db"""
    #     self.assertEqual(Collection.query.count(), 1)
    #     self.assertEqual(Collection.query.get(1).name, "Updated Collection")
