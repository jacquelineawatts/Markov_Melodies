from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

##############################################################################


def connect_to_db(app, db_uri="postgresql:///melodies"):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app

    connect_to_db(app)
    print "Connected to DB."

    from melody import Melody, MelodyNote
    from genre import Genre, MelodyGenre
    from note import Note, Duration
    from markov import Markov, Outcome
    from user import User, Connection, Like

    db.create_all()
