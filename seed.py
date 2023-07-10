from models import Collection, Entry
from app import db

db.drop_all()
db.create_all()

# Create a test collection
test_collection = Collection(id=1, description="TEST")

db.session.add(test_collection)
db.session.commit()