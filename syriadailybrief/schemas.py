from flask_marshmallow import Marshmallow
from marshmallow import fields

ma = Marshmallow()


class CollectionSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "name", "description", "created_at")

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=False)
    created_at = fields.Integer(dump_only=True)


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
