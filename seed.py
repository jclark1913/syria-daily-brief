from models import Collection, Entry
from app import db

db.drop_all()
db.create_all()

# Create a test collection
test_collection = Collection(name="Test_collection", description="TEST")
test_collection2 = Collection(name="Test_collection_2", description="TEST")

test_entry1 = Entry(collection_id=1, title="العنوان", publication="الموقع", full_text="هذا النص الكامل للمقالة باللغة العربية", link="google.com", date_posted="12385713")
test_entry2 = Entry(collection_id=1, title="2 العنوان", publication="الموقع", full_text="هذا النص الكامل للمقالة باللغة العربية", link="google.com", date_posted="12385713")
test_entry3 = Entry(collection_id=1, title="3 العنوان", publication="الموقع", full_text="هذا النص الكامل للمقالة باللغة العربية", link="google.com", date_posted="12385713")

db.session.add(test_collection)
db.session.add(test_collection2)
db.session.add(test_entry1)
db.session.add(test_entry2)
db.session.add(test_entry3)
db.session.commit()