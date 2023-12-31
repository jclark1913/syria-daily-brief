from flask_sqlalchemy import SQLAlchemy
import time

db = SQLAlchemy()


def connect_db(app):
    """Connects this database to Flask app.

    Called in app.py
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)


class Collection(db.Model):
    """The top-level table. A collection points to a specific grouping of
    scraped data."""

    __tablename__ = "collections"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = db.Column(
        db.String(200),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    created_at = db.Column(
        db.Integer,
        default=int(time.time()),
        nullable=False,
    )

    # Adds relationship between collection and its entries and vice-versa
    entries = db.relationship(
        "Entry", backref="collection", cascade="all, delete-orphan"
    )


class Entry(db.Model):
    """A single data point scraped from a website. Linked to a collection."""

    __tablename__ = "entries"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    collection_id = db.Column(
        db.Integer,
        db.ForeignKey("collections.id", ondelete="CASCADE"),
    )

    title = db.Column(
        db.Text,
        nullable=False,
    )

    title_translated = db.Column(
        db.Text,
        nullable=True,
    )

    publication = db.Column(
        db.Text,
        nullable=False,
    )

    full_text = db.Column(
        db.Text,
        nullable=True,
    )

    full_text_translated = db.Column(
        db.Text,
        nullable=True,
    )

    link = db.Column(
        db.Text,
    )

    date_posted = db.Column(
        db.Text,
    )

    ai_summary = db.Column(
        db.Text,
    )
