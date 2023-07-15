from models import Collection, Entry
from app import db

db.drop_all()
db.create_all()

# Create a test collection
test_collection = Collection(name="Test_collection", description="TEST")
test_collection2 = Collection(name="Test_collection_2", description="TEST")

db.session.add(test_collection)
db.session.add(test_collection2)
db.session.commit()