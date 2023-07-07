from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connects this database to Flask app.

    Called in app.py
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)