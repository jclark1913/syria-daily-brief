from flask_marshmallow import Marshmallow
from marshmallow import fields
from models import Collection, Entry

ma = Marshmallow()


class CollectionSchema(ma.Schema):
    name = fields.String(required=True)
    description = fields.String(required=False)

    class Meta:
        fields = ("id", "name", "description", "created_at")


class EntrySchema(ma.Schema):
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
