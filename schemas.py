from flask_marshmallow import Marshmallow
from marshmallow import fields
from models import Collection, Entry

ma = Marshmallow()


class CollectionSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=False)
    created_at = fields.Integer(dump_only=True)

    class Meta:
        fields = ("id", "name", "description", "created_at")


class EntrySchema(ma.Schema):

    id = fields.Integer(dump_only=True)
    collection_id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    title_translated = fields.String()
    publication = fields.String()
    full_text = fields.String()
    full_text_translated = fields.String()
    link = fields.String()
    date_posted = fields.String() #Update to date?
    ai_summary = fields.String()


    class Meta:
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
