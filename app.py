import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow

from models import db, connect_db, Collection, Entry

from schemas import CollectionSchema, EntrySchema

from marshmallow import ValidationError

import translation as translation

load_dotenv()

app = Flask(__name__)
ma = Marshmallow(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["JSON_SORT_KEYS"] = False
app.json.sort_keys = False

connect_db(app)

############# COLLECTIONS


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

    # Get JSON and load schema
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


@app.get("/api/collections/<int:collection_id>")
def get_collection(collection_id):
    """Returns a single collection as JSON.

    Returns: {id: 1, name: ..., ...}
    """

    collection = Collection.query.get_or_404(collection_id)
    collection_schema = CollectionSchema()
    result = collection_schema.dump(collection)

    return jsonify(result)


@app.post("/api/collections/<int:collection_id>")
def update_collection(collection_id):
    """Updates a given collection:

    Returns: {'message': 'Collection updated'}
    """

    data = request.get_json()
    curr_coll = Collection.query.get_or_404(collection_id)
    collection_schema = CollectionSchema()

    try:
        collection_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages)

    for field, value in data.items():
        if hasattr(curr_coll, field):
            setattr(curr_coll, field, value)

    db.session.commit()

    result = collection_schema.dump(curr_coll)

    return jsonify({"Collection updated": result})


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


# Translate multiple entries
# NOTE: This route may change. It is currently attached to a collection, but it
# doesn't access the collection_id at all nor is it dependent on anything save
# the PK of an entry. That being said, the user won't ever be translating
# multiple entries from more than one collection at a time.
@app.post("/api/collections/<int:collection_id>/entries/translate")
def translate_collection(collection_id):
    """Translates multiple entries from a collection using Argos translate and
    updates them in the db.

    Accepts: {"entry_ids": [1, 34, 34]}

    Returns: {"Translated":
                [{id: 1 ...}, ...]}
    """

    # Gets JSON from request
    data = request.get_json()

    # Gets list of entry ids
    entry_ids = data["entry_ids"]
    entry_schema = EntrySchema(many=True)

    # Filters for entry ids with query
    entries = Entry.query.filter(Entry.id.in_(entry_ids))

    # Translate all entries in list if list contains values
    if entries:
        translation.initialize_argostranslate()

        for e in entries:
            translation.translate_given_entry(e)

        db.session.commit()

    results = entry_schema.dump(entries)

    return jsonify({"Translated": results})


############# ENTRIES


@app.get("/api/collections/<int:collection_id>/entries/<int:entry_id>")
def get_single_entry(collection_id, entry_id):
    """Returns single entry from given collection

    Returns: {id: ..., title: ..., ...}
    """

    curr_entry = Entry.query.get_or_404(entry_id)
    entry_schema = EntrySchema()

    result = entry_schema.dump(curr_entry)

    return jsonify(result)


@app.post("/api/collections/<int:collection_id>/entries/<int:entry_id>")
def edit_single_entry(collection_id, entry_id):
    """Edits single entry from given collection

    Returns: {Entry updated}
    """

    data = request.get_json()
    curr_entry = Entry.query.get_or_404(entry_id)
    entry_schema = EntrySchema()

    try:
        entry_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages)

    for field, value in data.items():
        if hasattr(curr_entry, field):
            setattr(curr_entry, field, value)

    db.session.commit()

    result = entry_schema.dump(curr_entry)

    return jsonify({"Updated entry": result})


@app.post("/api/collections/<int:collection_id>/entries/<int:entry_id>/translate")
def translate_single_entry(collection_id, entry_id):
    """Translates single entry and updates its db instance"""

    curr_entry = Entry.query.get_or_404(entry_id)
    entry_schema = EntrySchema()

    # Initialize Argos Translation
    translation.initialize_argostranslate()

    # Translate entry
    translation.translate_given_entry(curr_entry)

    result = entry_schema.dump(curr_entry)

    return jsonify({"Translated": result})


# GET AI SUMMARY OF GIVEN ENTRY