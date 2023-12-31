import sys

import os

# Get the parent directory path (one level up from the current directory)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

from sdb.models import Collection, Entry
from sdb.app import db

db.drop_all()
db.create_all()

# Create a test collection
test_collection = Collection(name="Test_collection", description="TEST")
test_collection2 = Collection(name="Test_collection_2", description="TEST")

test_entry1 = Entry(
    collection_id=1,
    title="العنوان",
    publication="الموقع",
    full_text="هذا النص الكامل للمقالة الاولى باللغة العربية",
    link="google.com",
    date_posted="12385713",
)
test_entry2 = Entry(
    collection_id=1,
    title="2 العنوان",
    publication="الموقع",
    full_text="هذا النص الكامل للمقالة الثانية باللغة العربية",
    link="google.com",
    date_posted="12385713",
)
test_entry3 = Entry(
    collection_id=1,
    title="3 العنوان",
    publication="الموقع",
    full_text="هذا النص الكامل للمقالة الثالثة باللغة العربية",
    link="google.com",
    date_posted="12385713",
)

db.session.add(test_collection)
db.session.add(test_collection2)
db.session.add(test_entry1)
db.session.add(test_entry2)
db.session.add(test_entry3)
db.session.commit()
