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

