import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow

from models import db, connect_db, Collection, Entry

from schemas import CollectionSchema, EntrySchema

load_dotenv()

app = Flask(__name__)
ma = Marshmallow(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

connect_db(app)

############# COLLECTIONS


# GET ALL COLLECTIONS
@app.get("/api/collections")
def list_collections():
    """API route that returns all collections for a given user.

    Returns: [
        {id: 1, name: ..., ...},
        {id: 2, name: ..., ...},
        ...
        ]
    """

    data = Collection.query.all()
    collection_schema = CollectionSchema(many=True)
    result = collection_schema.dump(data)

    return jsonify(result)

    # collections = [collection.serialize() for collection in Collection.query.all()]

    # return jsonify(collections)


@app.post("/api/collections")
def create_new_collection():
    """API route that adds a new collection to the db and returns it.

    Returns: Added:[
        {id: 1, name:..., ...}
    ]

    """

    data = request.get_json()
    collection_schema = CollectionSchema()
    errors = collection_schema.validate(data)

    if errors:
        return jsonify({"errors": errors}), 400

    name = data["name"]
    description = data["description"]

    new_coll = Collection(name=name, description=description)
    db.session.add(new_coll)
    db.session.commit()

    result = collection_schema.dump(new_coll)

    return jsonify({"created": result})


# GET SINGLE COLLECTION

# UPDATE COLLECTION DETAILS

# DELETE COLLECTION
# Migrate entries in collection to another collection

# COPY FROM COLLECTION TO COLLECTION


############# ENTRIES

# GET ALL ENTRIES FOR GIVEN COLLECTION

# TRANSLATE GIVEN ENTRY

# GET AI SUMMARY OF GIVEN ENTRY
