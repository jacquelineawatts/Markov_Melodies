from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import numpy as np

db = SQLAlchemy()


class User(db.Model):
    """Class for App Users. """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    profile_img = db.Column(db.String(256))

    following = db.relationship('User',
                                secondary='connections',
                                primaryjoin='Connection.follower_user_id == User.user_id',
                                secondaryjoin='Connection.following_user_id == User.user_id',
                                backref=db.backref('followers'),
                                )

    def __repr__(self):
        return "<User ID: {}; User: {} {}; Email: {}>".format(self.user_id,
                                                              self.first_name,
                                                              self.last_name,
                                                              self.email,
                                                              )


class Melody(db.Model):
    """Class for generated Melodies"""

    __tablename__ = "melodies"

    melody_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30))
    is_major = db.Column(db.Boolean)
    key = db.Column(db.String(10))
    time_signature = db.Column(db.Float)
    path_to_midi_file = db.String(256)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    user = db.relationship('User', backref='melodies')

    genres = db.relationship("Genre",
                             secondary="melodies_genres",
                             backref='melodies')

    def __repr__(self):
        return "<Melody ID: {}, Title: {}, Key: {}>".format(self.melody_id,
                                                            self.title,
                                                            self.key,
                                                            )


class Note(db.Model):
    """Class for notes """

    __tablename__ = "notes"

    note_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pitch = db.Column(db.String(3))
    octave = db.Column(db.Integer)
    duration = db.Column(db.Float)

    def __repr__(self):
        return "<Note ID: {}, Note: {}{}>".format(self.note_id,
                                                  self.pitch,
                                                  self.octave,
                                                  )

    def show_name_with_octave(self):

        return (self.pitch + str(self.octave)).encode('latin-1')


def get_note_by_nameWithOctave(nameWithOctave):

        pitch = nameWithOctave[:-1]
        octave = nameWithOctave[-1]

        note = Note.query.filter_by(pitch=pitch, octave=octave)
        try:
            note = note.one()

        except NoResultFound:
            print "No note found."
            note = None

        except MultipleResultsFound:
            print "Multiple notes found."
            note = note.first()

        return note

class MelodyNote(db.Model):
    """Middle table associating a melody with its corresponding notes. Additional
    relevant fields include sequence (order of notes within a melody)."""

    __tablename__ = "melody_notes"

    melodynote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    melody_id = db.Column(db.Integer, db.ForeignKey('melodies.melody_id'))
    note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    sequence = db.Column(db.Integer)

    melody = db.relationship('Melody', backref='melody_notes')
    note = db.relationship('Note', backref='melody_notes', order_by='MelodyNote.sequence')

    def __repr__(self):
        return "<MelodyNote ID: {}, Melody: {}, Note: {}, Sequence: {} >".format(self.melodynote_id,
                                                                                 self.melody,
                                                                                 self.note,
                                                                                 self.sequency,
                                                                                 )


class Markov(db.Model):
    """Class for Markov chain keys"""

    __tablename__ = "markovs"

    markov_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    second_note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'))

    first_note = db.relationship('Note', foreign_keys=[first_note_id])
    second_note = db.relationship('Note', foreign_keys=[second_note_id])
    genre = db.relationship("Genre", backref='markovs')

    def __repr__(self):
        return "<Markov ID: {}, Bi-gram: {}, {}>".format(self.markov_id,
                                                         self.first_note,
                                                         self.second_note,
                                                         )

    def select_outcome(self):

        potential_outcomes = [(outcome, outcome.weight) for outcome in self.outcomes]
        outcomes = [outcome[0] for outcome in potential_outcomes]
        weights = [outcome[1] for outcome in potential_outcomes]
        total = float(sum(weights))
        probability = [weight/total for weight in weights]

        outcome_note = np.random.choice(outcomes, 1, p=probability)

        return outcome_note[0]


def get_markov_by_tuple(notes_tuple):

    print notes_tuple
    first_note = get_note_by_nameWithOctave(notes_tuple[0])
    print first_note
    second_note = get_note_by_nameWithOctave(notes_tuple[1])
    print second_note

    markov = Markov.query.filter_by(first_note_id=first_note.note_id, second_note_id=second_note.note_id)
    try:
        markov = markov.one()

    except NoResultFound:
        print "No Markov key for that tuple."
        markov = None

    except MultipleResultsFound:
        print "Mult Markov keys found for that tuple."
        markov = markov.first()

    return markov


class Outcome(db.Model):
    """Class for Markov potential values and their associated weights"""

    __tablename__ = "outcomes"

    outcome_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    markov_id = db.Column(db.Integer, db.ForeignKey('markovs.markov_id'))
    note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    weight = db.Column(db.Integer)

    markov = db.relationship('Markov', backref='outcomes')
    note = db.relationship('Note', backref='outcomes')

    def __repr__(self):
        return "<Outcome ID: {}, Markov: {}, Note: {}, Weight: {}>".format(self.outcome_id,
                                                                           self.markov,
                                                                           self.note,
                                                                           self.weight,
                                                                           )


class Genre(db.Model):
    """Class for musical genres."""

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre = db.Column(db.String(20))

    def __repr__(self):
        return "<Genre ID: {}, Genre: {}".format(self.genre_id,
                                                 self.genre,
                                                 )


class MelodyGenre(db.Model):
    """Association table connecting melodies and genres."""

    __tablename__ = "melodies_genres"

    melodygenre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    melody_id = db.Column(db.Integer, db.ForeignKey('melodies.melody_id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'))

    def __repr__(self):
        return "<MelodyGenre ID: {}, Melody: {}, Genre: {}".format(self.melodygenre_id,
                                                                   self.melody_id,
                                                                   self.genre_id,
                                                                   )


class Connection(db.Model):
    """Class for Connections; like an association table for Users to Users relationships?"""

    __tablename__ = "connections"

    connection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    following_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # follower = db.relationship("User", foreign_keys=[follower_user_id])
    # following = db.relationship("User", foreign_keys=[following_user_id])

    def __repr__(self):
        return "<Connection ID: {}, Follower: {}, Following: {}>".format(self.connection_id,
                                                                         self.follower_user_id,
                                                                         self.following_user_id,
                                                                         )


class Like(db.Model):
    """Class for Likes """

    __tablename__ = "likes"

    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    melody_id = db.Column(db.Integer, db.ForeignKey('melodies.melody_id'))

    user = db.relationship('User', backref='likes')
    melody = db.relationship('Melody', backref='likes')

    def __repr__(self):
        return "<Like ID: {}, User: {}, Melody: {}>".format(self.like_id,
                                                            self.user,
                                                            self.melody,
                                                            )


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

    db.create_all()
