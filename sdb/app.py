import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError

import sdb.ai_utils as ai_utils
from sdb.controller import (
    generate_excel_from_collection,
    ScraperMap,
    run_selected_scrapers,
    add_entries_to_db,
)
from sdb.models import db, connect_db, Collection, Entry
from sdb.schemas import (
    CollectionSchema,
    SummarizeSchema,
    EntrySchema,
    MigrateSchema,
    PrintSchema,
    TranslateSchema,
    ScrapeSchema
)
import sdb.translation as translation


# TODO: Consider Blueprints for API routes in Flask

load_dotenv()

app = Flask(__name__)
ma = Marshmallow(app)

# NOTE: Temporary fix while in development
CORS(app)

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
    result = collection_schema.load(data)

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

    collection_schema.load(data, partial=True)

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
    entries = curr_coll.entries
    entry_schema = EntrySchema(many=True)

    result = entry_schema.dump(entries)

    return jsonify({curr_coll.name: result})


############# ENTRIES


# TODO: Consider removing collections from route
@app.get("/api/entries/<int:entry_id>")
def get_single_entry(entry_id):
    """Returns single entry from given collection

    Returns: {id: ..., title: ..., ...}
    """

    curr_entry = Entry.query.get_or_404(entry_id)
    entry_schema = EntrySchema()

    result = entry_schema.dump(curr_entry)

    return jsonify(result)


@app.post("/api/entries/<int:entry_id>")
def edit_single_entry(entry_id):
    """Edits single entry

    Returns: {Entry updated: {id: ..., title: ..., ...}
    """

    data = request.get_json()
    curr_entry = Entry.query.get_or_404(entry_id)
    entry_schema = EntrySchema()

    entry_schema.load(data, partial=True)

    for field, value in data.items():
        if hasattr(curr_entry, field):
            setattr(curr_entry, field, value)

    db.session.commit()

    result = entry_schema.dump(curr_entry)

    return jsonify({"Updated entry": result})


@app.delete("/api/entries/<int:entry_id>")
def delete_single_entry(entry_id):
    """Deletes single entry

    Returns: {Entry deleted: entry_id}
    """

    curr_entry = Entry.query.get_or_404(entry_id)
    db.session.delete(curr_entry)

    db.session.commit()

    return jsonify({"Deleted entry": entry_id})


########### Special operations


@app.post("/api/migrate_entries")
def migrate_entries():
    """Adds entries to a given collection and returns updated collection.

    Returns: {'message': '2 entries added to collection. 1 entry deleted.'}
    """

    # Get JSON and load schema
    data = request.get_json()

    # Verify JSON schema
    migrate_schema = MigrateSchema()
    migrate_schema.load(data)

    # Get data from JSON
    entry_ids = data["entry_ids"]
    origin_collection_id = data["origin_collection_id"]
    destination_collection_id = data["destination_collection_id"]
    delete_on_move = data.get("delete_on_move", False)
    entry_schema = EntrySchema()

    # Verify collections exist
    origin_collection = Collection.query.get_or_404(origin_collection_id)
    destination_collection = Collection.query.get_or_404(destination_collection_id)

    # Get entries from db
    entries_original = Entry.query.filter(Entry.id.in_(entry_ids)).all()

    # Return error if no entries found
    if not entries_original:
        return jsonify({"error": "No entries found."}), 400

    # Destructure entries into list of dicts
    entries_dicts = [entry_schema.dump(entry) for entry in entries_original]

    # Update db
    add_entries_to_db(entries=entries_dicts, collection_id=destination_collection_id)

    message = f"{len(entries_dicts)} entries added to {destination_collection.name} from {origin_collection.name}."

    # Delete original entries if delete_on_move is True
    if delete_on_move:
        delete_message = f" {len(entries_original)} entries deleted from {origin_collection.name}."
        for entry in entries_original:
            db.session.delete(entry)
        db.session.commit()
        message += delete_message

    return (
        jsonify(message=message),
        200,
    )


# Translate multiple entries
@app.post("/api/translate")
def translate_entries():
    """Translates multiple entries from a collection using Argos translate and
    updates them in the db.

    Accepts: {"entry_ids": [1, 34, 34]}

    Returns: {"Translated":
                [{id: 1 ...}, ...]}
    """

    # Gets JSON from request
    data = request.get_json()

    # Validate JSON schema
    translate_schema = TranslateSchema()
    translate_schema.load(data)

    # Gets list of entry ids
    entry_ids = data["entry_ids"]
    entry_schema = EntrySchema(many=True)

    # Filters for entry ids with query
    entries = Entry.query.filter(Entry.id.in_(entry_ids))

    if not entries.all():
        return jsonify({"error": "No entries found."}), 400

    # Translate all entries in list if list contains values
    translation.initialize_argostranslate()

    for e in entries:
        [en_title, en_full_text] = translation.get_translated_entry_title_and_text(
            e
        )
        e.title_translated = en_title
        e.full_text_translated = en_full_text

    db.session.commit()

    results = entry_schema.dump(entries)

    return jsonify({"Translated": results})


# Summarize multiple entries
@app.post("/api/summarize")
def summarize_entries():
    """Uses the OpenAI API to summarize given entries and update them in the
    database

    Accepts: {"entry_ids": [1, 34, 34]}

    Returns: {"Summarized":
                [{id: 1 ...}, ...]}
    """

    # Load OpenAI API key (will return None if not found)
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Return error if no API key
    if not openai_api_key:
        return jsonify(error="No OpenAI API key found"), 400

    # Gets JSON from request
    data = request.get_json()

    # Validate JSON schema
    summarize_schema = SummarizeSchema()
    summarize_schema.load(data)

    # Gets list of entry ids
    entry_ids = data["entry_ids"]
    entry_schema = EntrySchema(many=True)

    # Filters for entry ids with query
    entries = Entry.query.filter(Entry.id.in_(entry_ids))

    # Return error if no entries found
    if not entries.all():
        return jsonify({"error": "No entries found."}), 400

    # Summarize all entries in list if list contains values
    if entries:
        for e in entries:
            e.ai_summary = ai_utils.get_ai_summary_for_arabic_text(e.full_text)

    db.session.commit()

    results = entry_schema.dump(entries)

    return jsonify({"Summarized": results})


# Print to excel


@app.post("/api/print")
def generate_excel():
    """Generates an excel and saves it to the server"""

    # Gets JSON from request
    data = request.get_json()

    # Verify and get JSON data
    print_schema = PrintSchema()
    print_schema.load(data)
    collection_id = data["collection_id"]

    # Verifies that collection exists
    Collection.query.get_or_404(collection_id)

    # Generates excel
    try:
        generate_excel_from_collection(collection_id)
    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify(message="Excel generated"), 200


# Scraping


@app.post("/api/scrape")
def scrape_data():
    """Scrapes data from selected websites and saves it to the database"""

    # Gets JSON from request
    data = request.get_json()

    # Validate JSON schema
    scrape_schema = ScrapeSchema()
    scrape_schema.load(data)

    # Gets parameters from request
    scraper_strings = data["selected_scrapers"]
    stop_timestamp = data["stop_timestamp"]
    collection_id = data["collection_id"]

    # Gets enums corresponding to strings in scraper_strings
    try:
        selected_scrapers = [ScraperMap[scraper_str] for scraper_str in scraper_strings]
    except KeyError as e:
        raise Exception(f"Scraper {e} not found.")

    # Activates scrapers
    try:
        run_selected_scrapers(
            selections=selected_scrapers,
            stop_timestamp=stop_timestamp,
            collection_id=collection_id,
        )
    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify({"message": "Scraping complete."}), 200


# Error handlers
@app.errorhandler(404)
def not_found(e):
    """404 Not Found page."""

    return jsonify(error=404, text=str(e)), 404


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    """Error handler for Marshmallow validation errors"""

    return jsonify(errors=err.messages), 400


@app.errorhandler(Exception)
def global_error_handler(e):
    """Global error handler"""

    return jsonify(error=str(e)), 400
