import os
from dotenv import load_dotenv

from flask import Flask

from models import db, connect_db, Collection, Entry

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

connect_db(app)

## COLLECTIONS

# GET ALL COLLECTIONS

# GET SINGLE COLLECTION

# UPDATE COLLECTION DETAILS

# DELETE COLLECTION
    # Migrate entries in collection to another collection

# COPY FROM COLLECTION TO COLLECTION


## ENTRIES

# GET ALL ENTRIES FOR GIVEN COLLECTION