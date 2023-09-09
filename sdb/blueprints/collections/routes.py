from flask import Blueprint, jsonify, request

from sdb.models import db, Collection
from sdb.schemas import CollectionSchema

collection = Blueprint("collection", __name__)


@collection.get("/")
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


@collection.post("/")
def create_collection():
    """API route that creates a new collection.

    Returns: {id: 1, name: ..., ...}
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


@collection.get("/<int:collection_id>")
def get_collection(collection_id):
    """API route that returns a single collection.

    Returns: {id: 1, name: ..., ...}
    """

    data = Collection.query.get(collection_id)
    collection_schema = CollectionSchema()
    result = collection_schema.dump(data)

    return jsonify(result)


@collection.post("/<int:collection_id>")
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


# TODO: Handle migration of entries when collection is deleted.
# TODO: Add better response message.
@collection.delete("/<int:collection_id>")
def delete_collection(collection_id):
    """Deletes a given collection:

    Returns: {'message': 'Collection deleted'}
    """

    curr_coll = Collection.query.get_or_404(collection_id)

    db.session.delete(curr_coll)
    db.session.commit()

    return jsonify({"message": "Deleted collection"})
