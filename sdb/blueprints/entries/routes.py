from flask import Blueprint, jsonify, request

from sdb.models import db, Entry
from sdb.schemas import EntrySchema

entry = Blueprint("entry", __name__)

@entry.get("/<int:entry_id>")
def get_single_entry(entry_id):
    """Returns single entry from given collection

    Returns: {id: ..., title: ..., ...}
    """

    curr_entry = Entry.query.get_or_404(entry_id)
    entry_schema = EntrySchema()

    result = entry_schema.dump(curr_entry)

    return jsonify(result)

@entry.post("/<int:entry_id>")
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

@entry.delete("/<int:entry_id>")
def delete_single_entry(entry_id):
    """Deletes single entry

    Returns: {"Deleted entry": entry_id}
    """

    curr_entry = Entry.query.get_or_404(entry_id)

    db.session.delete(curr_entry)
    db.session.commit()

    return jsonify({"Deleted entry": entry_id})

@entry.post("/search")
def search_entries():
    """Searches entries for given query

    Returns: {entries: [{id: ..., title: ..., ...}, ...]}

{
    "date_range": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD"
    },
    "search_terms": [
        {
            "term": "Syria",
            "columns": ["publication", "article_summary"]
        },
        {
            "term": "Russia",
            "columns": ["article_title"]
        }
        // ... add more search terms as needed
    ]
}

    """

    data = request.get_json()
    collection_id = data.get("collection_id")
    entries = Entry.query.filter_by(collection_id=collection_id)

    search_terms = data.get("search_terms", [])
    date_range = data.get("date_range", {})

    start_date = date_range.get("start_date")
    end_date = date_range.get("end_date")

    if start_date:
        entries = entries.filter(Entry.date >= start_date)
    if end_date:
        entries = entries.filter(Entry.date <= end_date)

    for term_info in search_terms:
        term = term_info.get("term")
        columns = term_info.get("columns", [])
        for col in columns:
            if hasattr(Entry, col):
                entries = entries.filter(getattr(Entry, col).ilike(f"%{term}%"))

    entries = entries.all()
    entry_schema = EntrySchema(many=True)
    result = entry_schema.dump(entries)

    return jsonify({"entries": result})

