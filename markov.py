from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from note import Note
import numpy as np
from genre import Genre
from note import Note, Duration


class Markov(db.Model):
    """This class contains all attributes and functionality for building and
    referencing the Markov chain keys. See Outcomes class for corresponding values."""

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
        print 'OUTCOME NOTE: ', outcome_note

        return outcome_note[0].note

    @classmethod
    def add_markov_to_db(cls, first_note_id, second_note_id, genre_id):
        """Adds new markov chain key to the db. """

        markov = Markov(first_note_id=first_note_id,
                        second_note_id=second_note_id,
                        genre_id=genre_id,
                        )
        db.session.add(markov)
        db.session.commit()
        print "Added new Markov key object to db."

        return markov

    @classmethod
    def get_markov_by_tuple(cls, notes_tuple, genres):

        print 'NOTES TUPLE:', notes_tuple
        first_note = notes_tuple[0]
        print 'FIRST NOTE:', first_note
        second_note = notes_tuple[1]
        print 'SECOND NOTE:', second_note

        try:
            pass
            markov = Markov.query.filter_by(first_note_id=first_note.note_id, second_note_id=second_note.note_id).one()

        except NoResultFound:
            print "No Markov key for that tuple."
            markov = None

        except MultipleResultsFound:
            print "Mult Markov keys found for that tuple."
            markov = Markov.query.filter_by(first_note_id=first_note.note_id, second_note_id=second_note.note_id).first()

        return markov


class Outcome(db.Model):
    """Class for potential Markov values and their associated weights. See
    Markov class for the corresponding keys."""

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

    @classmethod
    def add_outcome_to_db(cls, markov_id, outcome_note_id):
        """Adds new outcome instance to db."""

        outcome = Outcome(markov_id=markov_id,
                          note_id=outcome_note_id,
                          weight=1,
                          )
        db.session.add(outcome)
        db.session.commit()
        print "Added new outcome object to db."


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    db.create_all()
