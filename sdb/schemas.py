from flask_marshmallow import Marshmallow
from marshmallow import fields, validate

ma = Marshmallow()


class CollectionSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "name", "description", "created_at", "entries")

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False)
    created_at = fields.Integer(dump_only=True)
    entries: fields.Nested = fields.Nested("EntrySchema", many=True, dump_only=True)



class EntrySchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            "id",
            "collection_id",
            "title",
            "title_translated",
            "publication",
            "full_text",
            "full_text_translated",
            "link",
            "date_posted",
            "ai_summary",
        )

    id = fields.Integer(dump_only=True)
    collection_id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    title_translated = fields.String()
    publication = fields.String()
    full_text = fields.String()
    full_text_translated = fields.String()
    link = fields.String()
    date_posted = fields.String()  # Update to date?
    ai_summary = fields.String()


class MigrateSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            "entry_ids",
            "origin_collection_id",
            "destination_collection_id",
            "delete_on_move",
        )

    entry_ids = fields.List(fields.Integer(), required=True)
    origin_collection_id = fields.Integer(required=True)
    destination_collection_id = fields.Integer(required=True)
    delete_on_move = fields.Boolean(required=False)

class PrintSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ["collection_id"]

    collection_id = fields.Integer(required=True)


class TranslateSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ["entry_ids"]

    entry_ids = fields.List(fields.Integer(), required=True)


class SummarizeSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ["entry_ids"]

    entry_ids = fields.List(fields.Integer(), required=True)

class ScrapeSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            "collection_id",
            "selected_scrapers",
            "stop_timestamp",
        )

    collection_id = fields.Integer(required=True)
    selected_scrapers = fields.List(fields.String(), required=True)
    stop_timestamp = fields.Integer(required=True)