import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow

from models import db, connect_db, Collection, Entry

from schemas import CollectionSchema, EntrySchema

from marshmallow import ValidationError

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


@app.post("/api/collections")
def create_new_collection():
    """API route that adds a new collection to the db and returns it.

    Returns: created:[
        {id: 1, name:..., ...}
    ]

    """
    # Get JSOn and load schema
    data = request.get_json()
    collection_schema = CollectionSchema()

    # Attempt to validate JSON data
    try:
        result = collection_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages)

    # Get data for new db instance
    name = data["name"]
    description = data.get("description", "")

    # Update db
    new_coll = Collection(name=name, description=description)
    db.session.add(new_coll)
    db.session.commit()

    # Serialize and return new db instance
    result = collection_schema.dump(new_coll)

    return jsonify({"created": result})


# GET SINGLE COLLECTION
@app.get("/api/collections/<int:collection_id>")
def get_collection(collection_id):
    """Returns a single collection as JSON.

    Returns: {id: 1, name: ..., ...}

    """

    collection = Collection.query.get_or_404(collection_id)
    collection_schema = CollectionSchema()
    result = collection_schema.dump(collection)

    return jsonify(result)


# UPDATE COLLECTION DETAILS
@app.post("/api/collections/<int:collection_id>")
def update_collection(collection_id):
    """Updates a given collection:

    Returns: {'message': 'Collection updated'}
    """

    data = request.get_json()
    curr_coll = Collection.query.get_or_404(collection_id)
    collection_schema = CollectionSchema()

    try:
        result = collection_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages)

    for field, value in data.items():
        if hasattr(curr_coll, field):
            setattr(curr_coll, field, value)

    db.session.commit()

    return jsonify({"message": "Collection updated"})


# DELETE Collection
# TODO: Handle migration of entries when collection is deleted
@app.delete("/api/collections/<int:collection_id>")
def delete_collection(collection_id):
    """Deletes a given collection

    Returns: {'message': 'Collection deleted'}
    """

    curr_coll = Collection.query.get_or_404(collection_id)
    db.session.delete(curr_coll)

    db.session.commit()

    return jsonify({"message": "Deleted collection"})


# DELETE COLLECTION
# Migrate entries in collection to another collection

# COPY FROM COLLECTION TO COLLECTION


############# ENTRIES

# GET ALL ENTRIES FOR GIVEN COLLECTION
@app.get("/api/collections/<int:collection_id>/entries")
def get_entries_from_collection(collection_id):
    """Returns all entries from a given collection

    Returns: {'collection_name': {entry, entry, ...}}
    """

    curr_coll = Collection.query.get_or_404(collection_id)
    entries = Entry.query.filter_by(collection_id=collection_id)
    entry_schema = EntrySchema(many=True)

    result = entry_schema.dump(entries)

    return jsonify({curr_coll.name: result})


# TRANSLATE GIVEN ENTRY

# GET AI SUMMARY OF GIVEN ENTRY
