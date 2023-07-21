import os
from unittest import TestCase
from models import db, Collection, Entry

os.environ["DATABASE_URL"] = "postgresql:///sdb_test"

from app import app

db.drop_all()
db.create_all()


class CollectionModelTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""

        Collection.query.delete()
        Entry.query.delete()

        self.client = app.test_client()

        self.collection = Collection(
            name="Test Collection", description="Test Description"
        )
        db.session.add(self.collection)
        db.session.commit()

        self.collection_id = self.collection.id

    def tearDown(self):
        db.session.rollback()

    def test_collection_model(self):
        """Does basic model work?"""

        # Collection is created in setup
        self.assertEqual(self.collection.name, "Test Collection")
        self.assertEqual(self.collection.description, "Test Description")

    def test_collection_entry_relationship(self):
        """Does collection have entries and does "entries" relationship work?"""

        entry = Entry(
            title="Test Entry",
            collection_id=self.collection_id,
            publication="Test Publication",
        )

        db.session.add(entry)
        db.session.commit()

        self.assertEqual(self.collection.entries[0], entry)


class EntryModelTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""

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

        self.entry_id = self.entry.id

    def tearDown(self):
        db.session.rollback()

    def test_entry_model(self):
        """Does basic entry model work?"""

        # Entry is created in setup
        self.assertEqual(self.entry.title, "Test Entry")
        self.assertEqual(self.entry.collection_id, self.collection_id)
        self.assertEqual(self.entry.publication, "Test Publication")

    def test_entry_collection_relationship(self):
        """Does entry have a collection and does "collection" backref work?"""

        self.assertEqual(self.entry.collection, self.collection)

    def test_entry_collection_delete(self):
        """Does entry delete when collection is deleted?"""

        db.session.delete(self.collection)
        db.session.commit()

        self.assertEqual(Entry.query.count(), 0)

    def test_entry_delete(self):
        """Does entry delete when deleted?"""

        db.session.delete(self.entry)
        db.session.commit()

        self.assertEqual(Entry.query.count(), 0)
