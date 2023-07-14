import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify

from models import db, connect_db, Collection, Entry

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

connect_db(app)

############# COLLECTIONS


# GET ALL COLLECTIONS
@app.get("/api/collections")
def list_collections():
    """API Route that returns all collections for a given user.

    Returns: [
        {id: 1, name: ..., ...},
        {id: 2, name: ..., ...},
        ...
        ]
    """

    collections = [collection.serialize() for collection in Collection.query.all()]

    return jsonify(collections)


# GET SINGLE COLLECTION

# UPDATE COLLECTION DETAILS

# DELETE COLLECTION
# Migrate entries in collection to another collection

# COPY FROM COLLECTION TO COLLECTION


############# ENTRIES

# GET ALL ENTRIES FOR GIVEN COLLECTION

# TRANSLATE GIVEN ENTRY

# GET AI SUMMARY OF GIVEN ENTRY
