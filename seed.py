from models import Collection, Entry
from app import db

db.drop_all()
db.create_all()

db.session.commit()